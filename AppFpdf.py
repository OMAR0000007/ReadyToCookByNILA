import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import fitz
import csv

# Path to the JSON file
data_file = "products.json"

# Load categories and items from the JSON file
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                st.error("Error loading products.json. Please check the file for correct JSON format.")
                return {}
    return {}

# Save categories and items to the JSON file
def save_data(categories):
    with open(data_file, 'w', encoding='utf-8') as file:
        json.dump(categories, file, ensure_ascii=False, indent=4)

# Load existing data
categories = load_data()

# Get the next bill number
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

# Generate PDF bill
def generate_pdf(bill_number, customer_info, items, subtotal, discount, delivery_charge, grand_total, payment_method):
    customer_mobile = customer_info["mobile"]
    pdf_file = f'bill_{bill_number}_{customer_mobile}.pdf'
    document = fitz.open()
    page = document.new_page()

    # Define the positions and rectangle for text
    width, height = fitz.paper_size("letter")
    y_position = height - 20

    # Insert text with custom font
    def insert_text(page, text, pos, font_size=12):
        rect = fitz.Rect(pos[0], pos[1], pos[0] + 500, pos[1] + 50)
        html = f"""<div style="font-size:{font_size}px">{text}</div>"""
        page.insert_htmlbox(rect, html)

    # Title
    insert_text(page, "Customer Bill", (250, 0), font_size=16)
    y_position -= 30
    insert_text(page, "R e a d y  -  t o  -  C o o k  -  b y  -  ' N I L A '", (200, 20), font_size=12)
    y_position -= 20
    insert_text(page, "E-mail: readytocook1711@gmail.com", (201, 40), font_size=12)
    y_position -= 20
    insert_text(page, "Contact Number: 01842-235229, 01611-235228", (170, 60), font_size=12)
    y_position -= 40

    # Bill details
    insert_text(page, "========================================================================", (30, 100))
    y_position -= 20
    insert_text(page, f"Bill Number: {bill_number}", (30, 120))
    insert_text(page, f"Customer Unique Code: {customer_info['unique_code']}", (350, 120))
    y_position -= 20
    insert_text(page, "-------------------------------------------------------------------------------------------------------------------------------------------", (30, 140))
    y_position -= 20
    insert_text(page, f"Date: {customer_info['date']}", (30, 160))
    y_position -= 20
    insert_text(page, f"Customer Name: {customer_info['name']}", (30, 180))
    y_position -= 20
    insert_text(page, f"Customer Mobile Number: {customer_info['mobile']}", (30, 200))
    y_position -= 20
    insert_text(page, f"Customer Address: {customer_info['address']}", (30, 220))
    y_position -= 40
    insert_text(page, "-------------------------------------------------------------------------------------------------------------------------------------------", (30, 240))
    # Headers
    headers = ["Category", "Item", "Unit Price", "Quantity", "Total Price"]
    header_x = [30, 100, 350, 425, 500]
    for i, header in enumerate(headers):
        insert_text(page, header, (header_x[i], 260))
    y_position -= 20
    h = 280
    # Items
    for item in items:
        for i, value in enumerate(item[2:]):
            insert_text(page, str(value), (header_x[i], h))
        h += 20

    # Summary
    y_position -= 80
    insert_text(page, "-------------------------------------------------------------------------------------------------------------------------------------------", (30, 500))
    y_position -= 20
    insert_text(page, f"Subtotal: {subtotal} Tk", (30, 520))
    y_position -= 20
    insert_text(page, f"Discount: {discount} Tk", (30, 540))
    y_position -= 20
    insert_text(page, f"Delivery Charge: {delivery_charge} Tk", (30, 560))
    insert_text(page, f"Payment Method: {payment_method}", (350, 560))
    y_position -= 40
    insert_text(page, f"Grand Total: {grand_total} Tk", (30, 600))
    y_position -= 40
    
    # Note
    y_position -= 200
    insert_text(page, "Please check your products in front of the delivery man!", (150, 650))
    y_position -= 20
    insert_text(page, "No complaint will be accepted later!!", (190, 670))
    y_position -= 20
    insert_text(page, "THANK YOU!!!", (250, 690))

    # Add the logo image
    logo_path = "RCN.jpg"
    qr_path = "qr.jpg"
    try:
        logo_rect = fitz.Rect(30, 5, 130, 105)
        page.insert_image(logo_rect, filename=logo_path)
        
        qr_rect = fitz.Rect(500, 5, 580, 85)
        page.insert_image(qr_rect, filename=qr_path)
    except Exception as e:
        print(f"Error loading logo image: {e}")

    document.save(pdf_file)
    return pdf_file

# Generate PDF file
pdf_file_path = generate_pdf()

# Display download button
st.markdown(
    f'<a href="data:application/pdf;base64,{pdf_file_path}" download="generated_pdf.pdf">Download PDF</a>',
    unsafe_allow_html=True
)

# Save to CSV
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

# Save customer info
def save_customer_info(unique_code, customer_info):
    # Convert the date object to string
    customer_info["date"] = customer_info["date"].strftime("%Y-%m-%d")
    
    customers_data = {}
    if os.path.exists('customers.json'):
        with open('customers.json', 'r', encoding='utf-8') as file:
            try:
                customers_data = json.load(file)
            except json.JSONDecodeError:
                st.error("Error loading customers.json. Please check the file for correct JSON format.")
    customers_data[unique_code] = customer_info
    with open('customers.json', 'w', encoding='utf-8') as file:
        json.dump(customers_data, file, ensure_ascii=False, indent=4)

# Main application
def main():
    st.title("Ready to Cook by 'NILA'")
    st.sidebar.title("Menu")
    menu_options = ["Home", "Make Bill", "Customers Profile", "Settings"]
    menu_choice = st.sidebar.selectbox("Choose an option", menu_options)
    
    if menu_choice == "Home":
        st.image("RCN.jpg")
        st.write("Welcome to Ready to Cook by 'NILA'")
    
    elif menu_choice == "Make Bill":
        st.header("Make Bill")
        
        items = []
        
        with st.form(key="bill_form"):
            bill_number = get_next_bill_number()
            st.text(f"Bill Number: {bill_number}")
            customer_info = {
                "date": st.date_input("Date", datetime.today()),
                "name": st.text_input("Customer Name"),
                "mobile": st.text_input("Customer Mobile Number"),
                "address": st.text_input("Customer Address"),
                "unique_code": st.text_input("Customer Unique Code")
            }
            
            if not all(customer_info.values()):
                st.warning("All customer information fields must be filled.")
            
            category = st.selectbox("Category", list(categories.keys()))
            items_selected = st.multiselect("Items", categories.get(category, []))
            
            if items_selected:
                for item in items_selected:
                    unit_price = st.number_input(f"Unit Price of {item}", min_value=0.0, format="%f")
                    quantity = st.number_input(f"Quantity of {item}", min_value=1)
                    total_price = unit_price * quantity
                    items.append([category, item, unit_price, quantity, total_price])
            
            if items:
                df = pd.DataFrame(items, columns=["Category", "Item", "Unit Price", "Quantity", "Total Price"])
                st.dataframe(df)
            
            subtotal = sum(item[-1] for item in items)
            discount = st.number_input("Discount", min_value=0.0, format="%f")
            delivery_charge = st.number_input("Delivery Charge", min_value=0.0, format="%f")
            grand_total = subtotal - discount + delivery_charge
            st.text(f"Grand Total: {grand_total}")
            
            payment_method = st.radio("Payment Method", ["Cash", "bKash", "Nagad"])
            submit_button = st.form_submit_button("Generate Bill")
            
            if submit_button:
                if not all(customer_info.values()):
                    st.warning("All customer information fields must be filled.")
                elif not items:
                    st.warning("At least one item must be selected.")
                elif subtotal == 0:
                    st.warning("Subtotal must be greater than zero.")
                else:
                    pdf_file = generate_pdf(bill_number, customer_info, items, subtotal, discount, delivery_charge, grand_total, payment_method)
                    save_to_csv(items, discount, grand_total, payment_method, customer_info["unique_code"])
                    save_customer_info(customer_info["unique_code"], customer_info)
                    st.success(f"Bill generated and saved as {pdf_file}")

    elif menu_choice == "Customers Profile":
        st.header("Customers Profile")
        if os.path.exists('customers.json'):
            with open('customers.json', 'r', encoding='utf-8') as file:
                try:
                    customers_data = json.load(file)
                    st.write(customers_data)
                except json.JSONDecodeError:
                    st.error("Error loading customers.json. Please check the file for correct JSON format.")
        else:
            st.write("No customer data found.")
    
    elif menu_choice == "Settings":
        st.header("Settings")
        new_category = st.text_input("Add New Category")
        if new_category:
            if new_category not in categories:
                categories[new_category] = []
                save_data(categories)
                st.success(f"Category '{new_category}' added successfully!")
            else:
                st.warning(f"Category '{new_category}' already exists.")
        
        selected_category = st.selectbox("Select Category to Add Items", list(categories.keys()))
        if selected_category:
            new_item = st.text_input(f"Add New Item to '{selected_category}' Category")
            if new_item:
                if new_item not in categories[selected_category]:
                    categories[selected_category].append(new_item)
                    save_data(categories)
                    st.success(f"Item '{new_item}' added to category '{selected_category}' successfully!")
                else:
                    st.warning(f"Item '{new_item}' already exists in category '{selected_category}'.")

if __name__ == "__main__":
    main()
