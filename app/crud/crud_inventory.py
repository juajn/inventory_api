# app/crud/crud_inventory.py
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.models.product import Product


def get_inventory_by_product(db: Session, product_id: int):
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def create_or_update_inventory(db: Session, product_id: int, quantity: int):
    inv = get_inventory_by_product(db, product_id)
    if inv:
        inv.quantity = quantity
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv
    else:
        inv = Inventory(product_id=product_id, quantity=quantity)
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv


def adjust_inventory(db: Session, product_id: int, delta: int):
    inv = get_inventory_by_product(db, product_id)
    if not inv:
        inv = Inventory(product_id=product_id, quantity=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)

    inv.quantity += delta
    if inv.quantity < 0:
        inv.quantity = 0
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv
