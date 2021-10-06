# -*- coding: utf-8 -*-
from typing import Optional
import random

import pytest
import gilded_rose as gr
from gilded_rose import Item, GildedRose


def assert_sell_in_quality(name: str, sell_in: int, quality: int, days: int, expected_sell_in: Optional[int] = None,
                           expected_quality: Optional[int] = None) -> None:
    """
    Check whether expected quality and/or sell_in is present after an amount of days
    Args:
        sell_in: The sellIn before
        quality: The quality before
        expected_sell_in: The expected sellIn after the days
        expected_quality: The expected quality after the days
        name: The name of the product
        days: The amount of days
    """
    assert expected_quality is not None or expected_sell_in is not None, "Must assert at least one of quality or sellIn"
    items = [Item(name, sell_in, quality)]
    gilded_rose = GildedRose(items)
    for i in range(0, days):
        gilded_rose.update_quality()
    assert expected_quality is None or expected_quality == items[0].quality, f"Unexpected quality for product {name}"
    assert expected_sell_in is None or expected_sell_in == items[0].sell_in, f"Unexpected sellIn for product {name}"


def test_foo_item_should_decrease_quality_and_sell_in_by_1_after_a_day():
    assert_sell_in_quality("foo", sell_in=5, quality=4, days=1, expected_sell_in=4, expected_quality=3)


def test_sell_in_goes_negative():
    assert_sell_in_quality("foo", sell_in=1, quality=5, days=2, expected_sell_in=-1)


def test_quality_degrades_twice_as_fast_after_sell_in():
    """
    With a sell-in of 1 after 2 days we degrade quality once normally and once double.
    """
    assert_sell_in_quality("foo", sell_in=1, quality=5, days=2, expected_quality=2)


def test_quality_is_never_negative_but_stays_at_0():
    """
    Interpreting negative as strict negative.
    """
    assert_sell_in_quality("foo", sell_in=5, quality=1, days=1 + random.randint(1, 100), expected_quality=0)


def test_aged_brie_increased_quality_when_it_gets_older():
    assert_sell_in_quality(gr.AGED_BRIE, sell_in=2, quality=0, days=1, expected_sell_in=1, expected_quality=1)


def test_quality_never_more_than_50():
    nr_days = random.randint(1, 100)
    assert_sell_in_quality(gr.AGED_BRIE, sell_in=100, quality=50, days=nr_days, expected_sell_in=100-nr_days,
                           expected_quality=50)


random_int_test_data = [
    (random.randint(-10, 100)) for _ in range(0, 100)
]


@pytest.mark.parametrize("sell_in", random_int_test_data)
def test_sulfuras_does_not_change(sell_in: int):
    nr_days = random.randint(1, 100)
    quality = random.randint(-10, 100)
    assert_sell_in_quality(gr.SULFURAS, sell_in=sell_in, quality=quality, days=nr_days,
                           expected_sell_in=sell_in, expected_quality=quality)


@pytest.mark.parametrize("sell_in", [i for i in range(11, 15)])
def test_back_stage_pass_increases_by_1_if_more_than_10_days_left(sell_in):
    start_quality = random.randint(10, 20)
    assert_sell_in_quality(gr.BACKSTAGE, sell_in=sell_in, quality=start_quality, days=1, expected_sell_in=sell_in-1,
                           expected_quality=start_quality+1)


@pytest.mark.parametrize("sell_in", [i for i in range(6, 11)])
def test_back_stage_pass_increases_by_2_if_10_or_less_but_more_than_5_days_left(sell_in):
    start_quality = random.randint(10, 20)
    assert_sell_in_quality(gr.BACKSTAGE, sell_in=sell_in, quality=start_quality, days=1, expected_sell_in=sell_in-1,
                           expected_quality=start_quality+2)


@pytest.mark.parametrize("sell_in", [i for i in range(1, 6)])
def test_back_stage_pass_increases_by_2_if_10_or_less_but_more_than_5_days_left(sell_in):
    start_quality = random.randint(10, 20)
    assert_sell_in_quality(gr.BACKSTAGE, sell_in=sell_in, quality=start_quality, days=1, expected_sell_in=sell_in-1,
                           expected_quality=start_quality+3)


def test_back_stage_pass_drops_to_zero_after_concert():
    start_quality = random.randint(10, 20)
    assert_sell_in_quality(gr.BACKSTAGE, sell_in=0, quality=start_quality, days=1, expected_sell_in=-1,
                           expected_quality=0)
