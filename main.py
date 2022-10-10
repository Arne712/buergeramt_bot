from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
import os
import time
import schedule

EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PWD = os.environ.get("EMAIL_PWD")

def main():
    schedule.every(2).hours.do(scheduled_job)
    while True:
        schedule.run_pending()
        time.sleep(1800)

def document_initialised(driver):
    return driver.execute_script("return initialised")

def scheduled_job():
    found_appointment = appointment_available()
    send_email(found_appointment)

def appointment_available():
    driver =  webdriver.Chrome()
    driver.get('https://stadt-karlsruhe.saas.smartcjm.com/m/stadt-karlsruhe-standesamt/extern/calendar/?uid=6385cdf9-0825-4d94-bff2-d4f1315f05f1&lang=de')
    button_section = driver.find_element(By.CLASS_NAME, "counter")
    buttons = button_section.find_elements(By.CLASS_NAME, "counterButton")
    for button in buttons:
        if button.text == "+":
            plus_button = button

    plus_button.click()

    continue_button = driver.find_element(By.ID, "forward-service")
    continue_button.click()

    saturday_checkbox = driver.find_element(By.ID, "weekdays_6")
    saturday_checkbox.click()

    sunday_checkbox = driver.find_element(By.ID, "weekdays_0")
    sunday_checkbox.click()

    buttons = driver.find_elements(By.CLASS_NAME, "button.ui.primary.right.labeled.icon.button")

    for button in buttons:
        if button.id == "forward-service":
            break
        elif button.id == "first_next_btn":
            break
        else:
            continue_button_2 = button

    continue_button_2.click()

    appointments = driver.find_element(By.ID, "appointment_holder")
    appointment = appointments.find_element(By.TAG_NAME, "h3")
    print(appointment.text[0:50])

    if appointment.text[0:50] == "Leider sind aktuell keine freien Termine verfügbar":
        return False
    else:
        return True

    driver.quit()

def send_email(found_appointment):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_ADDRESS, EMAIL_PWD)

        if found_appointment:
            subject = "Es gibt einen freien Termin!"
            body = "Es gibt einen freien Termin beim Bürgeramt. Klicke hier: https://stadt-karlsruhe.saas.smartcjm.com/m/stadt-karlsruhe-standesamt/extern/calendar/?uid=6385cdf9-0825-4d94-bff2-d4f1315f05f1&wsid=110f4e3f-58ab-4994-ba49-722b3fbc95c9&lang=de"
        else:
            subject = "Kein neuer Termin frei"
            body = "Es wurde kein neuer Termin gefunden."

        msg = f"Subject: {subject}\n\n{body}"

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)

main()