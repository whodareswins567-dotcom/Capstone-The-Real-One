from pydantic import BaseModel, Field


class InventoryItemBase(BaseModel):
    sku: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    category: str = Field(min_length=2, max_length=80)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)
    location: str = Field(min_length=2, max_length=120)
    notes: str | None = Field(default=None, max_length=500)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=2, max_length=40)
    name: str | None = Field(default=None, min_length=2, max_length=120)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, min_length=2, max_length=120)
    notes: str | None = Field(default=None, max_length=500)


class InventoryItem(InventoryItemBase):
    id: int
    created_at: str
    updated_at: str
    low_stock: bool
