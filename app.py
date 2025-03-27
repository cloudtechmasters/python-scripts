from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from contextlib import contextmanager
import mysql.connector

# FastAPI app
app = FastAPI()

# MySQL connection configuration
db_config = {
    "host": "localhost",  # Change to MySQL server host
    "user": "root",
    "password": "my-secret-pw",
    "database": "mysql",
    "port": 3306
}

# Context manager for MySQL connection
@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        yield cursor, conn
    finally:
        cursor.close()
        conn.close()

# Pydantic model for Customer
class Customer(BaseModel):
    id: int  # Add id to the model
    name: str
    country_of_birth: str
    country_of_residence: str
    segment: str

    class Config:
        orm_mode = True  # This is necessary to allow FastAPI to read data from a database row

# Create table if not exists (run once to set up the database)
@app.on_event("startup")
def startup_db():
    with get_db_connection() as (cursor, conn):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                country_of_birth VARCHAR(50),
                country_of_residence VARCHAR(50),
                segment VARCHAR(50)
            )
        """)
        conn.commit()

# Create customer
@app.post("/customers/", response_model=Customer)
def create_customer(customer: Customer):
    with get_db_connection() as (cursor, conn):
        cursor.execute(
            "INSERT INTO customers (name, country_of_birth, country_of_residence, segment) "
            "VALUES (%s, %s, %s, %s)",
            (customer.name, customer.country_of_birth, customer.country_of_residence, customer.segment)
        )
        conn.commit()
    return customer

# Read all customers
@app.get("/customers/", response_model=List[Customer])
def get_customers():
    with get_db_connection() as (cursor, conn):
        cursor.execute("SELECT id, name, country_of_birth, country_of_residence, segment FROM customers")
        customers = cursor.fetchall()
        return [Customer(id=id, name=name, country_of_birth=country_of_birth,
                         country_of_residence=country_of_residence, segment=segment)
                for id, name, country_of_birth, country_of_residence, segment in customers]

# Read customer by ID
@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    with get_db_connection() as (cursor, conn):
        cursor.execute("SELECT id, name, country_of_birth, country_of_residence, segment FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return Customer(id=customer[0], name=customer[1], country_of_birth=customer[2],
                        country_of_residence=customer[3], segment=customer[4])

# Update customer
@app.put("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, customer: Customer):
    with get_db_connection() as (cursor, conn):
        cursor.execute(
            "UPDATE customers SET name=%s, country_of_birth=%s, country_of_residence=%s, segment=%s WHERE id=%s",
            (customer.name, customer.country_of_birth, customer.country_of_residence, customer.segment, customer_id)
        )
        conn.commit()
        return customer

# Delete customer
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    with get_db_connection() as (cursor, conn):
        cursor.execute("DELETE FROM customers WHERE id=%s", (customer_id,))
        conn.commit()
    return {"message": "Customer deleted successfully"}
