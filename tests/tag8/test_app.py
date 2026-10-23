from my_sum import my_sum
import pytest


@pytest.mark.parametrize('werte', [(1, 2, 3), (5, 7, 12)])
def test_sum_returns_correct_value(werte):
	assert my_sum(werte[0],werte[1]) == werte[2]
    
def test_sum_fail():
    with pytest.raises(TypeError, match="can only concat"):
	    my_sum('hello', 2)