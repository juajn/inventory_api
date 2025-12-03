# app/crud/crud_product.py
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str):
    return db.query(Product).filter(Product.sku == sku).first()


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, product_in: ProductCreate):
    product = Product(name=product_in.name, sku=product_in.sku, price=product_in.price, description=product_in.description)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: dict):
    for field, value in data.items():
        setattr(product, field, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product):
    db.delete(product)
    db.commit()
