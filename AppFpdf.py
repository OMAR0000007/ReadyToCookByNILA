import streamlit as st
import json
import os
import csv
from datetime import datetime
from fpdf import FPDF
import pandas as pd

# Path to the JSON file
data_file = "products.json"
categories = {}

# Function to load categories and items from the JSON file
def load_data():
    global categories
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as file:
                categories = json.load(file)
        except json.JSONDecodeError:
            categories = {}

# Function to save categories and items to the JSON file
def save_data():
    with open(data_file, 'w', encoding='utf-8') as file:
        json.dump(categories, file, ensure_ascii=False, indent=4)

# Load existing data
load_data()

def get_next_bill_number():
    if os.path.exists('bill_number.txt'):
        with open('bill_number.txt', 'r') as file:
            bill_number = int(file.read().strip())
    else:
        bill_number = 20240001
    bill_number += 1
    with open('bill_number.txt', 'w') as file:
        file.write(str(bill_number))
    return bill_number

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Customer Bill', 0, 1, 'C')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "R e a d y   t o   C o o k   b y   ' N I L A '", 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, "E-mail: readytocook1711@gmail.com", 0, 1, 'C')
        self.cell(0, 10, "Contact Number: 01842-235229, 01611-235228", 0, 1, 'C')

def generate_pdf(bill_number, customer_info, items, total_price, discount, delivery_charge, grand_total):
    customer_mobile = customer_info['mobile']
    pdf_file = f'bill_{bill_number}_{customer_mobile}.pdf'

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    pdf.cell(0, 10, "========================================================================", 0, 1)
    pdf.cell(0, 10, f"Bill Number: {bill_number}", 0, 1)
    pdf.cell(0, 10, f"Customer Unique Code: {customer_info['unique_code']}", 0, 1)
    pdf.cell(0, 10, "---------------------------------------------------------------------------------------", 0, 1)
    pdf.cell(0, 10, f"Date: {customer_info['date']}", 0, 1)
    pdf.cell(0, 10, f"Customer Name: {customer_info['name']}", 0, 1)
    pdf.cell(0, 10, f"Customer Mobile Number: {customer_mobile}", 0, 1)
    pdf.cell(0, 10, f"Customer Address: {customer_info['address']}", 0, 1)

    headers = ["Category", "Item", "Unit Price", "Quantity", "Total Price"]
    header_widths = [40, 60, 40, 30, 30]

    for i, header in enumerate(headers):
        pdf.cell(header_widths[i], 10, header, 1)

    pdf.ln()

    for item in items:
        for i, value in enumerate(item):
            pdf.cell(header_widths[i], 10, str(value), 1)
        pdf.ln()

    pdf.cell(0, 10, "---------------------------------------------------------------------------------------", 0, 1)
    pdf.cell(0, 10, f"Subtotal: {total_price} Tk", 0, 1)
    pdf.cell(0, 10, f"Discount: {discount} Tk", 0, 1)
    pdf.cell(0, 10, f"Delivery Charge: {delivery_charge} Tk", 0, 1)
    pdf.cell(0, 10, f"Payment Method: {customer_info['payment_method']}", 0, 1)
    pdf.cell(0, 10, f"Grand Total: {grand_total} Tk", 0, 1)

    pdf.cell(0, 10, "Please check your products in front of the delivery man!", 0, 1)
    pdf.cell(0, 10, "No complaint will be accepted later!!", 0, 1)
    pdf.cell(0, 10, "THANK YOU!!!", 0, 1)

    pdf.output(pdf_file)
    return pdf_file

def save_to_csv(items, discount, grand_total, payment_method, unique_code):
    file_exists = os.path.exists('sales_data.csv')
    with open('sales_data.csv', 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Date", "Mobile", "Address", "Category", "Item", "Unit Price",
                "Quantity", "Total Price", "Discount", "Grand Total", "Payment Method", "Customer Unique Code"
            ])
        for item in items:
            writer.writerow(item + [discount, grand_total, payment_method, unique_code])

def save_customer_info(unique_code, customer_info):
    customers_data = {}

    if os.path.exists('customers.json'):
        try:
            with open('customers.json', 'r', encoding='utf-8') as file:
                customers_data = json.load(file)
        except json.JSONDecodeError:
            customers_data = {}

    customers_data[unique_code] = customer_info

    with open('customers.json', 'w', encoding='utf-8') as file:
        json.dump(customers_data, file, ensure_ascii=False, indent=4)

def save_bill_and_data(bill_number, customer_info, items, total_price, discount, delivery_charge, grand_total):
    unique_code = customer_info['unique_code']
    customer_info['total_spend'] = total_price

    customers_data = {}
    if os.path.exists('customers.json'):
        try:
            with open('customers.json', 'r', encoding='utf-8') as file:
                customers_data = json.load(file)
        except json.JSONDecodeError:
            customers_data = {}

    if unique_code in customers_data:
        customers_data[unique_code]['total_spend'] += total_price
    else:
        customers_data[unique_code] = customer_info

    with open('customers.json', 'w', encoding='utf-8') as file:
        json.dump(customers_data, file, ensure_ascii=False, indent=4)

    pdf_file = generate_pdf(bill_number, customer_info, items, total_price, discount, delivery_charge, grand_total)
    save_to_csv(items, discount, grand_total, customer_info['payment_method'], unique_code)
    return pdf_file

def main():
    st.title("Ready to Cook by 'NILA'")

    page = st.sidebar.selectbox("Choose a page", ["Home", "Make Bill", "Customer Profile", "Settings"])

    if page == "Home":
        st.write("Welcome to 'Ready to Cook by NILA'!")
        st.image("RCN.jpg", width=300)
    
    elif page == "Make Bill":
        st.header("Make a Bill")
        
        date = st.date_input("Date", datetime.today())
        customer_name = st.text_input("Customer Name")
        customer_mobile = st.text_input("Customer Mobile Number")
        customer_address = st.text_input("Customer Address")
        unique_code = st.text_input("Customer Unique Code")
        
        category = st.selectbox("Category", list(categories.keys()))
        items = categories.get(category, [])
        item_name = st.selectbox("Item Name", items)
        unit_price = st.number_input("Unit Price", min_value=0.0, step=0.01)
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
        item_total = unit_price * quantity

        add_item_button = st.button("Add Item")

        if 'items_list' not in st.session_state:
            st.session_state.items_list = []

        if add_item_button:
            st.session_state.items_list.append([category, item_name, unit_price, quantity, item_total])
            st.success(f"Added {item_name} to the list")

        discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=0.01)
        delivery_charge = st.number_input("Delivery Charge", min_value=0.0, step=0.01)
        payment_method = st.selectbox("Payment Method", ["Bkash", "Nagad", "Rocket", "Upay", "COD"])

        if st.session_state.items_list:
            st.write("Items in the Bill:")
            items_df = pd.DataFrame(
                st.session_state.items_list,
                columns=["Category", "Item Name", "Unit Price", "Quantity", "Total Price"]
            )
            st.write(items_df)

            total_price = sum(item[4] for item in st.session_state.items_list)
            st.write(f"Total Price: {total_price:.2f} Tk")

            discount_amount = (discount / 100) * total_price
            grand_total = total_price - discount_amount + delivery_charge
            st.write(f"Grand Total: {grand_total:.2f} Tk")

        if st.button("Generate Bill"):
            bill_number = get_next_bill_number()
            customer_info = {
                'date': str(date),
                'name': customer_name,
                'mobile': customer_mobile,
                'address': customer_address,
                'unique_code': unique_code,
                'payment_method': payment_method
            }
            pdf_file = save_bill_and_data(
                bill_number, customer_info, st.session_state.items_list, total_price, discount, delivery_charge, grand_total
            )
            st.success(f"Bill generated successfully! Bill Number: {bill_number}")
            st.write("Download the bill PDF from the link below:")
            with open(pdf_file, "rb") as file:
                btn = st.download_button(
                    label="Download Bill PDF",
                    data=file,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

    elif page == "Customer Profile":
        st.header("Customer Profile")
        unique_code = st.text_input("Enter Customer Unique Code")

        if st.button("Load Profile"):
            customers_data = {}
            if os.path.exists('customers.json'):
                try:
                    with open('customers.json', 'r', encoding='utf-8') as file:
                        customers_data = json.load(file)
                except json.JSONDecodeError:
                    st.warning("The customer data file is empty or corrupted!")
                    customers_data = {}
            
            if unique_code in customers_data:
                customer_info = customers_data[unique_code]
                st.write("Customer Information")
                st.write(f"Name: {customer_info['name']}")
                st.write(f"Mobile Number: {customer_info['mobile']}")
                st.write(f"Address: {customer_info['address']}")
                st.write(f"Total Spend: {customer_info.get('total_spend', 0)} Tk")
            else:
                st.warning("Customer not found!")

    elif page == "Settings":
        st.header("Settings")
        
        category = st.text_input("Category Name")
        item_name = st.text_input("Item Name")

        if st.button("Add Item to Category"):
            if category in categories:
                categories[category].append(item_name)
            else:
                categories[category] = [item_name]
            save_data()
            st.success(f"Added {item_name} to {category}")

        st.write("Current Categories and Items")
        st.write(categories)

if __name__ == "__main__":
    main()
