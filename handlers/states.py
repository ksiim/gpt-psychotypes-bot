from aiogram.fsm.state import State, StatesGroup


class SpamState(StatesGroup):
    text = State()
    confirmation = State()


class EditState(StatesGroup):
    waiting_for_new_text = State()
    waiting_for_new_const_value = State()
    
class AddPsychotypeState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_prompt = State()
    waiting_for_model = State()
    
class ChangePsychotypeState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_prompt = State()
    
    
class PackageChangePropertiesState(StatesGroup):
    waiting_for_count = State()
    waiting_for_price = State()
    
    
class AddChannelState(StatesGroup):
    link = State()
    message = State()
    name = State()


class DalleState(StatesGroup):
    waiting_for_description = State()