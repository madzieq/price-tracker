*** Settings ***
Library     SeleniumLibrary
Resource    ../resources/keywords.robot
Resource    ../resources/variables.robot

Suite Setup     Otwórz aplikację
Suite Teardown  Zamknij aplikację

*** Test Cases ***
Użytkownik może dodać nowy produkt
    Przejdź do dashboardu
    Kliknij przycisk "Dodaj produkt"
    Wypełnij formularz produktu    ${TEST_PRODUCT_NAME}    ${TEST_PRODUCT_URL}
    Zatwierdź formularz
    Strona powinna zawierać produkt    ${TEST_PRODUCT_NAME}

Formularz waliduje pusty URL
    Przejdź do dashboardu
    Kliknij przycisk "Dodaj produkt"
    Wypełnij formularz produktu    Test Product    ${EMPTY}
    Zatwierdź formularz
    Page Should Contain    URL jest wymagany

Formularz waliduje nieprawidłowy URL
    Przejdź do dashboardu
    Kliknij przycisk "Dodaj produkt"
    Wypełnij formularz produktu    Test Product    nie-jest-url
    Zatwierdź formularz
    Page Should Contain    Nieprawidłowy URL

Użytkownik może ustawić alert cenowy dla produktu
    Przejdź do dashboardu
    Strona powinna zawierać produkt    ${TEST_PRODUCT_NAME}
    Click Element    xpath://div[contains(text(),'${TEST_PRODUCT_NAME}')]
    Ustaw alert cenowy    ${TEST_THRESHOLD}    ${TEST_EMAIL}
