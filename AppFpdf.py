import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz
import csv

# Global variables
categories = {}

# Load categories and items from the JSON file
def load_data():
    global categories
    data_file = "products.json"
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as file:
            categories = json.load(file)

# Save categories and items to the JSON file
def save_data():
    data_file = "products.json"
    with open(data_file, 'w', encoding='utf-8') as file:
        json.dump(categories, file, ensure_ascii=False, indent=4)

# Generate PDF bill
def generate_pdf(bill_number, customer_info, items, totals):
    customer_mobile = customer_info['mobile']
    pdf_file = f'bill_{bill_number}_{customer_mobile}.pdf'
    document = fitz.open()
    page = document.new_page()
    width, height = fitz.paper_size("letter")

    # Define the positions and rectangle for text
    y_position = height - 20

    # Title
    page.insert_text((250, 0), "Customer Bill", fontsize=16)
    page.insert_text((200, 20), "Ready to Cook by 'NILA'", fontsize=12)
    page.insert_text((201, 40), "E-mail: readytocook1711@gmail.com", fontsize=12)
    page.insert_text((170, 60), "Contact Number: 01842-235229, 01611-235228", fontsize=12)
    y_position -= 30

    # Bill details
    page.insert_text((30, 100), "========================================================================")
    page.insert_text((30, 120), f"Bill Number: {bill_number}")
    page.insert_text((350, 120), f"Customer Unique Code: {customer_info['unique_code']}")
    page.insert_text((30, 140), "-------------------------------------------------------------------------------------------------------------------------------------------")
    page.insert_text((30, 160), f"Date: {customer_info['date']}")
    page.insert_text((30, 180), f"Customer Name: {customer_info['name']}")
    page.insert_text((30, 200), f"Customer Mobile Number: {customer_mobile}")
    page.insert_text((30, 220), f"Customer Address: {customer_info['address']}")
    page.insert_text((30, 240), "-------------------------------------------------------------------------------------------------------------------------------------------")

    # Headers
    headers = ["Category", "Item", "Unit Price", "Quantity", "Total Price"]
    header_x = [30, 100, 350, 425, 500]
    for i, header in enumerate(headers):
        page.insert_text((header_x[i], 260), header, fontsize=12)

    # Items
    h = 280
    for item in items:
        for i, value in enumerate(item):
            page.insert_text((header_x[i], h), str(value), fontsize=12)
        h += 20

    # Summary
    page.insert_text((30, 500), "-------------------------------------------------------------------------------------------------------------------------------------------")
    page.insert_text((30, 520), f"Subtotal: {totals['subtotal']} Tk")
    page.insert_text((30, 540), f"Discount: {totals['discount']} Tk")
    page.insert_text((30, 560), f"Delivery Charge: {totals['delivery_charge']} Tk")
    page.insert_text((350, 560), f"Payment Method: {totals['payment_method']}")
    page.insert_text((30, 600), f"Grand Total: {totals['grand_total']} Tk")

    # Note
    page.insert_text((150, 650), "Please check your products in front of the delivery man!")
    page.insert_text((190, 670), "No complaint will be accepted later!!")
    page.insert_text((250, 690), "THANK YOU!!!")

    document.save(pdf_file)
    return pdf_file

# Save to CSV
def save_to_csv(items, totals, customer_info):
    file_exists = os.path.exists('sales_data.csv')
    with open('sales_data.csv', 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Date", "Mobile", "Address", "Category", "Item", "Unit Price",
                "Quantity", "Total Price", "Discount", "Grand Total", "Payment Method", "Customer Unique Code"
            ])
        for item in items:
            writer.writerow(item + [totals['discount'], totals['grand_total'], totals['payment_method'], customer_info['unique_code']])

# Streamlit app
def main():
    st.title("Ready to Cook by 'NILA'")
    load_data()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Make Bill", "Customer Profiles", "Settings"])

    if page == "Home":
        st.header("Welcome to Ready to Cook by 'NILA'")
        st.image("path/to/your/image.jpg", use_column_width=True)
        st.write("Please use the sidebar to navigate through the options.")
    
    elif page == "Make Bill":
        st.header("Make a Bill")
        bill_number = get_next_bill_number()
        st.write(f"Bill Number: {bill_number}")

        customer_info = {}
        customer_info['date'] = st.date_input("Date", datetime.today())
        customer_info['name'] = st.text_input("Customer Name")
        customer_info['mobile'] = st.text_input("Customer Mobile Number")
        customer_info['address'] = st.text_input("Customer Address")
        customer_info['unique_code'] = st.text_input("Customer Unique Code")

        # Item entry
        st.subheader("Add Items")
        category = st.selectbox("Category", list(categories.keys()))
        item = st.selectbox("Item", categories.get(category, []))
        unit_price = st.number_input("Unit Price", min_value=0.0, format="%f")
        quantity = st.number_input("Quantity", min_value=0.0, format="%f")

        if st.button("Add Item"):
            total_price = unit_price * quantity
            items.append([customer_info['date'], customer_info['mobile'], customer_info['address'], category, item, unit_price, quantity, total_price])
            st.success(f"Added {quantity} of {item} to the bill.")

        # Display items
        if items:
            st.subheader("Items")
            df_items = pd.DataFrame(items, columns=["Date", "Mobile", "Address", "Category", "Item", "Unit Price", "Quantity", "Total Price"])
            st.table(df_items)

            # Calculate totals
            subtotal = sum(item[7] for item in items)
            discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, format="%f")
            discount_amount = subtotal * (discount / 100)
            delivery_charge = st.number_input("Delivery Charge", min_value=0.0, format="%f")
            payment_method = st.selectbox("Payment Method", ["COD", "bKash", "Nagad", "Card"])
            grand_total = subtotal - discount_amount + delivery_charge

            totals = {
                "subtotal": subtotal,
                "discount": discount_amount,
                "delivery_charge": delivery_charge,
                "payment_method": payment_method,
                "grand_total": grand_total
            }

            st.subheader("Totals")
            st.write(f"Subtotal: {subtotal} Tk")
            st.write(f"Discount: {discount_amount} Tk")
            st.write(f"Delivery Charge: {delivery_charge} Tk")
            st.write(f"Grand Total: {grand_total} Tk")

            if st.button("Save Bill and Data"):
                pdf_file = generate_pdf(bill_number, customer_info, items, totals)
                save_to_csv(items, totals, customer_info)
                st.success(f"Bill saved as {pdf_file} and data saved to CSV.")
                items.clear()

    elif page == "Customer Profiles":
        st.header("Customer Profiles")
        unique_code = st.text_input("Enter Customer Unique Code")
        
        if st.button("Search"):
            customers_data = load_customers()
            customer = customers_data.get(unique_code)
            if customer:
                st.write(f"Date: {customer['date']}")
                st.write(f"Name: {customer['name']}")
                st.write(f"Mobile: {customer['mobile']}")
                st.write(f"Address: {customer['address']}")
                st.write(f"Total Spend: {customer['total_spend']}")
            else:
                st.error("Customer not found!")

    elif page == "Settings":
        st.header("Settings")
        st.subheader("Manage Categories and Items")

        # Add category
        new_category = st.text_input("Add Category")
        if st.button("Add Category"):
            if new_category:
                categories[new_category] = []
                save_data()
                st.success(f"Category '{new_category}' added.")

        # Remove category
        remove_category = st.selectbox("Remove Category", list(categories.keys()))
        if st.button("Remove Category"):
            if remove_category:
                del categories[remove_category]
                save_data()
                st.success(f"Category '{remove_category}' removed.")

        # Add item to category
        selected_category = st.selectbox("Select Category to Add Item", list(categories.keys()))
        new_item = st.text_input("Add Item to Selected Category")
        if st.button("Add Item"):
            if new_item:
                categories[selected_category].append(new_item)
                save_data()
                st.success(f"Item '{new_item}' added to category '{selected_category}'.")

if __name__ == "__main__":
    items = []
    main()
