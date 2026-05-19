*** Settings ***
Library     SeleniumLibrary
Library     RequestsLibrary
Resource    ../resources/keywords.robot
Resource    ../resources/variables.robot

Suite Setup     Otwórz aplikację
Suite Teardown  Zamknij aplikację

*** Test Cases ***
Dashboard powinien się załadować
    Przejdź do dashboardu
    Page Should Contain    Price Tracker
    Page Should Contain Element    css:.stats

Dashboard pokazuje statystyki produktów
    Przejdź do dashboardu
    Page Should Contain Element    css:[data-testid="stat-products"]
    Page Should Contain Element    css:[data-testid="stat-alerts"]
    Page Should Contain Element    css:[data-testid="stat-savings"]

Przycisk dodaj produkt jest widoczny
    Przejdź do dashboardu
    Page Should Contain Button    Dodaj produkt

API health check działa
    Sprawdź API health

*** Keywords ***
Przejdź do dashboardu
    Go To    ${BASE_URL}
    Wait Until Page Contains    Price Tracker    timeout=${TIMEOUT}
