import streamlit as st
import datetime

st.title("Know Your Age")
today = datetime.date.today()
dob = st.date_input("Enter Date of Birth" ,
              min_value=datetime.date(1800,1,1) ,
                max_value=datetime.date.today()
             )

st.write(f"selected DOB is {dob} ")

cal_age = st.button("Calculate your age")
if cal_age:
    age = dob.year - today.year
    st.success(f"Your Age is {age}")