from state import Dialog


def check_output(text, **kwargs):
    print(text)


def test_init_dialog():
    d = Dialog(check_output)

    assert d.state == 'start'

    d.on_start_trigger()

    return d


def test_right_dialog():
    d = test_init_dialog()

    assert d.state == 'size'

    d.handle_message('Большую')

    assert d.state == 'pay'

    d.handle_message('картой')

    assert d.state == 'confirm'

    d.handle_message('да')

    assert d.state == 'final'


def test_wrong_dialog():
    d = test_init_dialog()

    assert d.state == 'size'

    d.handle_message('some-wrong-text')

    assert d.state == 'size'


def test_cancel_order():
    d = test_init_dialog()

    assert d.state == 'size'

    d.handle_message('маленькую')

    assert d.state == 'pay'

    d.handle_message('наличкой')

    assert d.state == 'confirm'

    d.handle_message('нет')

    assert d.state == 'size'
