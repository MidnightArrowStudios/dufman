from __future__ import annotations
from typing import Self

from ..enums import LibraryType
from ..library import find_library_containing_asset_id
from ..url import AssetAddress


class FormulaMap:

    def __init__(self:FormulaMap, figure_id:str, url:str) -> Self:
        self.property_urls:list[str] = []
        self._collate_property_urls(url)
        return


    def _collate_property_urls(self:FormulaMap, url:str) -> None:

        address:AssetAddress = AssetAddress.create_from_url(url)

        library_type:LibraryType = find_library_containing_asset_id(url)
        print(library_type)
        return
