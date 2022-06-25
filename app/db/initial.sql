create type ShopUnitType as enum ('OFFER','CATEGORY');
create table if not exists items
(
    shop_type ShopUnitType,
    id uuid constraint items_pk primary key,
    name_item text not null,
    price integer,
    parent_id uuid references items(id) on delete cascade null,
    date_update  timestamp with time zone not null,
    count_offer integer
);