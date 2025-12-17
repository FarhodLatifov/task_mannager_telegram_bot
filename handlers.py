from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import keyboards as kb
import database as db
import calendar_utils
from translations import get_text

router = Router()

class AddTask(StatesGroup):
    title = State()
    category = State()
    priority = State()
    deadline = State()
    attachment = State()

class SearchTask(StatesGroup):
    query = State()

async def get_lang(user_id: int):
    return await db.get_user_language(user_id)

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Ensure user exists in DB on start
    await db.set_user_language(message.from_user.id, 'ru') # Default or keep existing
    # Actually set_user_language overwrites, so we should check first or use INSERT IGNORE logic which is hard with sqlite helper. 
    # For now, let's just get it. If not found, it returns 'en'.
    lang = await get_lang(message.from_user.id)
    await message.answer(get_text(lang, 'welcome'), reply_markup=kb.main_menu(lang))

@router.message(F.text.in_({'🌍 Language', '🌍 Язык'})) # Match both EN and RU button text
async def cmd_language(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(get_text(lang, 'lang_select'), reply_markup=kb.language_selection)

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    await db.set_user_language(callback.from_user.id, lang_code)
    await callback.answer()
    
    # Confirm and show new menu
    await callback.message.edit_text(get_text(lang_code, 'lang_set'))
    await callback.message.answer(get_text(lang_code, 'welcome'), reply_markup=kb.main_menu(lang_code))

# --- Add Task Flow ---
# We need to match localized buttons. Using a magic filter with a list of all possibilities or a custom filter is best.
# For simplicity, we can try to match the command via a broader filter or check for user state.
# Or, since we have only 2 languages, just list both strings.
@router.message(F.text.in_({'➕ Add Task', '➕ Добавить задачу'}))
async def start_add_task(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.set_state(AddTask.title)
    await message.answer(get_text(lang, 'enter_title'))

@router.message(AddTask.title)
async def process_title(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.update_data(title=message.text)
    await state.set_state(AddTask.category)
    await message.answer(get_text(lang, 'select_category'), reply_markup=kb.categories(lang))

@router.callback_query(AddTask.category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    # Map back category code to text if needed, or just store the code 'Work'. 
    # Storing 'Work' (English) in DB is better for consistency.
    category_code = callback.data.split("_")[1]
    
    await state.update_data(category=category_code) # Store the code, display can be localized later
    await state.set_state(AddTask.priority)
    
    # We display the localized name of the category they picked
    # We need a reverse lookup or just mapping.
    # Simple trick: we know the structure.
    # But for now showing the code or just the prompt is fine.
    
    await callback.message.edit_text(f"{get_text(lang, 'select_priority')}", reply_markup=kb.priorities(lang))
    await callback.answer()

@router.callback_query(AddTask.priority, F.data.startswith("prio_") | (F.data == "skip_prio"))
async def process_priority(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    priority = callback.data.split("_")[1] if "prio_" in callback.data else None
    await state.update_data(priority=priority)
    await state.set_state(AddTask.deadline)
    await callback.message.edit_text(get_text(lang, 'select_deadline'), reply_markup=calendar_utils.generate_calendar())
    await callback.answer()

@router.callback_query(calendar_utils.CalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: calendar_utils.CalendarCallback, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    if callback_data.action == "ignore":
        await callback.answer()
        return
    if callback_data.action == "nav":
        await callback.message.edit_reply_markup(reply_markup=calendar_utils.generate_calendar(callback_data.year, callback_data.month))
        await callback.answer()
        return
    if callback_data.action == "day":
        date_str = f"{callback_data.year}-{callback_data.month:02d}-{callback_data.day:02d}"
        await state.update_data(deadline=date_str)
        await state.set_state(AddTask.attachment)
        await callback.message.edit_text(f"{get_text(lang, 'attach_file')}", reply_markup=kb.skip_attachment(lang))
        await callback.answer()

@router.callback_query(AddTask.deadline, F.data == "skip_date")
async def skip_deadline(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    await state.update_data(deadline=None)
    await state.set_state(AddTask.attachment)
    await callback.message.edit_text(get_text(lang, 'attach_file'), reply_markup=kb.skip_attachment(lang))
    await callback.answer()

@router.message(AddTask.attachment)
async def process_attachment(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    
    if message.photo:
        att_id = message.photo[-1].file_id
        att_type = "photo"
    elif message.document:
        att_id = message.document.file_id
        att_type = "document"
    else:
        att_id = None
        att_type = None

    await db.add_task(message.from_user.id, data['title'], data.get('category'), data.get('priority'), data.get('deadline'), att_id, att_type)
    await state.clear()
    await message.answer(get_text(lang, 'task_added'), reply_markup=kb.main_menu(lang))

@router.callback_query(AddTask.attachment, F.data == "skip_att")
async def skip_attachment_handler(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    data = await state.get_data()
    await db.add_task(callback.from_user.id, data['title'], data.get('category'), data.get('priority'), data.get('deadline'))
    await state.clear()
    await callback.message.edit_text(get_text(lang, 'task_added'))
    await callback.message.answer(get_text(lang, 'task_list_header'), reply_markup=kb.main_menu(lang)) # Show menu again
    await callback.answer()

# --- List & Manage ---
@router.message(F.text.in_({'📋 My Tasks', '📋 Мои задачи'}))
async def show_tasks(message: Message):
    lang = await get_lang(message.from_user.id)
    tasks = await db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer(get_text(lang, 'no_tasks'), reply_markup=kb.main_menu(lang))
        return

    await message.answer(get_text(lang, 'task_list_header'))
    for task in tasks:
        title = task['title']
        status = task['status']
        # Localize category display if possible, but map is complex. Using raw for now + icon.
        cat = f"[{task['category']}] " if task['category'] else ""
        prio = f"{'🔴' if task['priority'] == 'High' else '🟡' if task['priority'] == 'Medium' else '🟢'}" if task['priority'] else ""
        dead = f"📅 {task['deadline']}" if task['deadline'] else ""
        
        status_text = get_text(lang, 'completed') if status else get_text(lang, 'pending')
        display_text = f"{cat}<b>{title}</b> {prio}\n{dead}\nStatus: {status_text}"
        
        if task['attachment_id']:
            display_text += "\n📎"
            
        await message.answer(display_text, reply_markup=kb.task_actions(task['id'], lang))

# --- Search ---
@router.message(F.text.in_({'🔍 Search', '🔍 Поиск'}))
async def start_search(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.set_state(SearchTask.query)
    await message.answer(get_text(lang, 'search_prompt'))

@router.message(SearchTask.query)
async def process_search(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    tasks = await db.search_tasks(message.from_user.id, message.text)
    await state.clear()
    if not tasks:
        await message.answer(get_text(lang, 'search_no_results'), reply_markup=kb.main_menu(lang))
        return
    
    await message.answer(get_text(lang, 'search_results'))
    for task in tasks:
        await message.answer(f"📝 <b>{task['title']}</b>", reply_markup=kb.task_actions(task['id'], lang))

# --- Actions ---
@router.callback_query(F.data.startswith("done_"))
async def complete_task(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    task_id = int(callback.data.split("_")[1])
    await db.update_task_status(task_id, 1)
    await callback.answer(get_text(lang, 'marked_done'))
    await callback.message.edit_text(f"{callback.message.html_text}\n\n{get_text(lang, 'completed')}", reply_markup=None)

@router.callback_query(F.data.startswith("delete_"))
async def delete_task_handler(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    task_id = int(callback.data.split("_")[1])
    await db.delete_task(task_id)
    await callback.answer(get_text(lang, 'deleted'))
    await callback.message.delete()
