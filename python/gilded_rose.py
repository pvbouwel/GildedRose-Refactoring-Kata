# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

AGED_BRIE = "Aged Brie"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"


class GildedRose(object):
    MAX_QUALITY = 50

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name not in ITEM_UPDATERS:
                DefaultAgingUpdater().update_item(item)
            else:
                ITEM_UPDATERS[item.name].update_item(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)


class SellInUpdater(ABC):
    @abstractmethod
    def get_new_sell_in(self, sell_in: int) -> int:
        """
        This method has to calculate the new amount of days to the sell-by date.
        Args:
            sell_in: amount of days to the sell-by date before end of day

        Returns:
            The new sell_in
        """
        pass


class QualityUpdater(ABC):
    # The default minimum quality should be positive
    DEFAULT_MINIMUM_QUALITY = 0
    # The default maximum quality a product can reach, if set to None no enforcement is done.
    DEFAULT_MAXIMUM_QUALITY = 50

    OPT_MINIMUM_QUALITY = "minimum_quality"
    OPT_MAXIMUM_QUALITY = "maximum_quality"

    def __init__(self, *args, **kwargs):
        self.minimum_quality = kwargs.get(self.OPT_MINIMUM_QUALITY, self.DEFAULT_MINIMUM_QUALITY)
        # A maximum quality that can be reached if set to None no limit is set
        self.maximum_quality = kwargs.get(self.OPT_MAXIMUM_QUALITY, self.DEFAULT_MAXIMUM_QUALITY)

    @abstractmethod
    def _get_new_quality(self, quality: int, sell_in: int) -> int:
        """
        This method has to calculate the new quality based of the old quality and the amount of days to the sell-by date
        Args:
            quality: Quality before end of day
            sell_in: amount of days to the sell-by date before end of day

        Returns:
            The new quality
        """
        pass

    def enforce_maximum_quality(self, quality):
        if self.maximum_quality is not None and quality > self.maximum_quality:
            return self.maximum_quality
        else:
            return quality

    def enforce_minimum_quality(self, quality):
        if self.minimum_quality is not None and quality < self.minimum_quality:
            return self.minimum_quality
        else:
            return quality

    def get_new_quality(self, quality: int, sell_in: int) -> int:
        new_quality = self._get_new_quality(quality=quality, sell_in=sell_in)
        return self.enforce_minimum_quality(self.enforce_maximum_quality(new_quality))


class ItemUpdater(QualityUpdater, SellInUpdater, ABC):
    def update_item(self, item: Item):
        """
        Method that updates an item. An item is mutable and will be changed in place.
        Args:
            item: The original item before end of day.

        Returns:
            The item how it will be after the end of day.
        """
        item.quality = self.get_new_quality(item.quality, item.sell_in)
        item.sell_in = self.get_new_sell_in(item.sell_in)

    def get_new_sell_in(self, sell_in: int) -> int:
        """
        Default implementation to calculate the new amount of sell_in days where each day there is one day less to sell
        the item.
        Args:
            sell_in: The sell_in days before end of day.

        Returns:
            The sell_in days after end of day.
        """
        return sell_in - 1


class DefaultAgingUpdater(ItemUpdater):
    """
    By default quality decreases when time passes
    """
    QUALITY_DEGRADATION_BEFORE_SELL_DATE = 1
    QUALITY_DEGRADATION_AFTER_SELL_DATE = 2
    
    def _get_new_quality(self, quality: int, sell_in: int) -> int:
        if sell_in > 0:
            return quality - self.QUALITY_DEGRADATION_BEFORE_SELL_DATE
        else:
            return quality - self.QUALITY_DEGRADATION_AFTER_SELL_DATE


class MaturingProductUpdater(ItemUpdater):
    """
    For a maturing Product quality always increases.
    """
    def _get_new_quality(self, quality: int, sell_in: int) -> int:
        return quality + 1


class NoSellInUpdates(SellInUpdater):
    """
    An updater that never changes the sell_in value
    """
    def get_new_sell_in(self, sell_in: int) -> int:
        return sell_in


class LegendaryProductUpdater(NoSellInUpdates, ItemUpdater):
    """
    For Legendary Items no updates need to be done.
    """
    def __init__(self, *args, **kwargs):
        kwargs[ItemUpdater.OPT_MAXIMUM_QUALITY] = None
        kwargs[ItemUpdater.OPT_MINIMUM_QUALITY] = None
        super(LegendaryProductUpdater, self).__init__(*args, **kwargs)

    def _get_new_quality(self, quality: int, sell_in: int) -> int:
        return quality


class EventProductUpdater(ItemUpdater):
    """
    For events we follow the logic
    """
    EVENT_PASSED_VALUE = 0
    CLOSE_TO_EVENT_THRESHOLD_IN_DAYS = 10
    FINAL_CHANCE_THRESHOLD_IN_DAYS = 5
    DEFAULT_INCREMENTOR = 1
    CLOSE_INCREMENTOR = 2
    FINAL_CHANCE_INCREMENTOR = 3

    def _get_new_quality(self, quality: int, sell_in: int) -> int:
        if sell_in == 0:
            return self.EVENT_PASSED_VALUE
        elif sell_in <= self.FINAL_CHANCE_THRESHOLD_IN_DAYS:
            return quality + self.FINAL_CHANCE_INCREMENTOR
        elif sell_in <= self.CLOSE_TO_EVENT_THRESHOLD_IN_DAYS:
            return quality + self.CLOSE_INCREMENTOR
        else:
            return quality + self.DEFAULT_INCREMENTOR


ITEM_UPDATERS = {
    AGED_BRIE: MaturingProductUpdater(),
    SULFURAS: LegendaryProductUpdater(),
    BACKSTAGE: EventProductUpdater()
}
