from transitions import Machine, State
from telegram import ReplyKeyboardMarkup


def get_reply_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup.from_row(buttons_list)
    keyboard.one_time_keyboard = True
    keyboard.selective = True
    keyboard.resize_keyboard = True
    return keyboard


class SizeEnum:
    BIG = 'большую'
    SMALL = 'маленькую'


class PaymentEnum:
    CASH = 'наличкой'
    CARD = 'картой'


class ConfirmEnum:
    YES = 'да'
    NO = 'нет'


class PizzaOrder:
    def __init__(self):
        self.size = None
        self.pay_method = None



class Dialog(object):
    StartState = State(name='start') # A start state purposed to invoke it's transition manually (on_start_trigger)
    SizeState = State(name='size')
    PayState = State(name='pay')
    ConfirmState = State(name='confirm')
    FinalState = State(name='final')

    keyboard_markups = {
        'size': [SizeEnum.SMALL, SizeEnum.BIG],
        'pay': [PaymentEnum.CARD, PaymentEnum.CASH],
        'confirm': [ConfirmEnum.NO, ConfirmEnum.YES],
        'final': None
    }

    cur_reply_keyboard = None

    def __init__(self, send_message_func):
        self.send_message = send_message_func
        self.pizza_order = PizzaOrder()

        self.SizeState.on_enter = [self.on_size_state]
        self.PayState.on_enter = [self.on_pay_state]
        self.ConfirmState.on_enter = [self.on_confirm_state]
        self.FinalState.on_enter = [self.on_final_state]

        states = [self.StartState, self.SizeState, self.PayState, self.ConfirmState, self.FinalState]
        self.machine = Machine(model=self, states=states, initial=self.StartState)

        """
        For every method starts with "on_", the following code will create additional one with suffix "_trigger"
        This is to invoke transitions for self.machine object
        """

        self.machine.add_transition('on_start_trigger',         'start',    'size')
        self.machine.add_transition('on_big_chosen_trigger',    'size',     'pay')
        self.machine.add_transition('on_small_chosen_trigger',  'size',     'pay')
        self.machine.add_transition('on_cash_chosen_trigger',   'pay',      'confirm')
        self.machine.add_transition('on_card_chosen_trigger',   'pay',      'confirm')
        self.machine.add_transition('on_confirmed_trigger',     'confirm',  'final')
        self.machine.add_transition('on_cancelled_trigger',     'confirm',  'size')

    def handle_message(self, text: str):
        """
        A basic method that is the only input passing to Dialog class
        It may be either user messages or strings written manually or from tests 
        """

        transitions_map = [
            # Income text       Necessary state     Call on appropriate state
            (SizeEnum.SMALL,    self.SizeState,     self.on_small_chosen),
            (SizeEnum.BIG,      self.SizeState,     self.on_big_chosen),
            (PaymentEnum.CASH,  self.PayState,      self.on_cash_chosen),
            (PaymentEnum.CARD,  self.PayState,      self.on_card_chosen),
            (ConfirmEnum.YES,   self.ConfirmState,  self.on_confirmed),
            (ConfirmEnum.NO,    self.ConfirmState,  self.on_cancelled),
        ]

        flag = False
        for i in transitions_map:
            if text.lower() == i[0] and self.state == i[1].name:
                i[2].__call__()
                flag = True
        if not flag:
            self.send_message('Wrong answer, try again')

    def update_keyboard_markup(self):
        """
        Update reply keyboard with current state
        """
        buttons_list = self.keyboard_markups[self.state]

        if not buttons_list: self.cur_reply_keyboard = None; return

        self.cur_reply_keyboard = get_reply_keyboard(buttons_list)

    # --- Methods invoked on entering one of the state

    def on_size_state(self):
        self.update_keyboard_markup()
        self.send_message('Какую вы хотите пиццу? Большую или маленькую?', reply_markup=self.cur_reply_keyboard)

    def on_pay_state(self):
        self.update_keyboard_markup()
        self.send_message('Как вы будете платить?', reply_markup=self.cur_reply_keyboard)

    def on_confirm_state(self):
        self.update_keyboard_markup()
        self.send_message(f'Вы хотите {self.pizza_order.size} пиццу, оплата - {self.pizza_order.pay_method}?', reply_markup=self.cur_reply_keyboard)

    def on_final_state(self):
        self.update_keyboard_markup()
        self.cur_reply_keyboard = None
        self.send_message('Спасибо за заказ', reply_markup=self.cur_reply_keyboard)

    # --- Methods called invoked manually for every needed transition

    def on_big_chosen(self):
        self.send_message(f'Вы выбрали большую пиццу')
        self.pizza_order.size = SizeEnum.BIG
        self.on_big_chosen_trigger()
        return True

    def on_small_chosen(self):
        self.send_message(f'Вы выбрали маленькую пиццу')
        self.pizza_order.size = SizeEnum.SMALL
        self.on_small_chosen_trigger()
        return True

    def on_cash_chosen(self):
        self.pizza_order.pay_method = PaymentEnum.CASH
        self.on_cash_chosen_trigger()
        return True

    def on_card_chosen(self):
        self.pizza_order.pay_method = PaymentEnum.CARD
        self.on_card_chosen_trigger()
        return True

    def on_confirmed(self):
        self.on_confirmed_trigger()
        return True

    def on_cancelled(self):
        self.on_cancelled_trigger()
        return True
