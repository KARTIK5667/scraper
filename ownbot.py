# import os
# import streamlit as st
# import Apifile

# from langchain.document_loaders import TextLoader
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.llms import OpenAI
# from langchain.chat_models import ChatOpenAI

# # Set OPENAI_API_KEY
# os.environ["OPENAI_API_KEY"] = Apifile.API

# # Create Streamlit app
# st.title("Chatbot App")

# # Input field for user query
# query = st.text_input("Enter your query:")

# # Load the text document
# loader = TextLoader('stocks.csv')

# # Create an instance of ChatOpenAI
# chat_openai_instance = ChatOpenAI()

# # Create an index from the loader
# index = VectorstoreIndexCreator().from_loaders([loader])

# # Check if query is not empty
# if query:
#     # Perform query and get the response
#     response = index.query(query, chat_openai_instance)
    
#     # Display the response
#     st.write("Chatbot Response:")
#     st.write(response)


import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import Apifile

def scrape_stock(driver, ticker_symbol):
        # build the URL of the target page
    url = f'https://finance.yahoo.com/quote/{ticker_symbol}'

    # visit the target page
    driver.get(url)

    try:
        # wait up to 3 seconds for the consent modal to show up
        consent_overlay = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.consent-overlay')))

        # click the 'Accept all' button
        accept_all_button = consent_overlay.find_element(By.CSS_SELECTOR, '.accept-all')
        accept_all_button.click()
    except TimeoutException:
        print('Cookie consent overlay missing')

    # initialize the dictionary that will contain
    # the data collected from the target page
    stock = { 'ticker': ticker_symbol }

    # scraping the stock data from the price indicators
    regular_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketPrice"]') \
        .text
    regular_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChange"]') \
        .text
    regular_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')

    post_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketPrice"]') \
        .text
    post_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketChange"]') \
        .text
    post_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')

    stock['regular_market_price'] = regular_market_price
    stock['regular_market_change'] = regular_market_change
    stock['regular_market_change_percent'] = regular_market_change_percent
    stock['post_market_price'] = post_market_price
    stock['post_market_change'] = post_market_change
    stock['post_market_change_percent'] = post_market_change_percent

    # scraping the stock data from the "Summary" table
    previous_close = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PREV_CLOSE-value"]').text
    open_value = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="OPEN-value"]').text
    bid = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BID-value"]').text
    ask = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="ASK-value"]').text
    days_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DAYS_RANGE-value"]').text
    week_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="FIFTY_TWO_WK_RANGE-value"]').text
    volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="TD_VOLUME-value"]').text
    avg_volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="AVERAGE_VOLUME_3MONTH-value"]').text
    market_cap = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="MARKET_CAP-value"]').text
    beta = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BETA_5Y-value"]').text
    pe_ratio = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PE_RATIO-value"]').text
    eps = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EPS_RATIO-value"]').text
    earnings_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EARNINGS_DATE-value"]').text
    dividend_yield = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DIVIDEND_AND_YIELD-value"]').text
    ex_dividend_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EX_DIVIDEND_DATE-value"]').text
    year_target_est = driver.find_element(By.CSS_SELECTOR,
                                          '#quote-summary [data-test="ONE_YEAR_TARGET_PRICE-value"]').text

    stock['previous_close'] = previous_close
    stock['open_value'] = open_value
    stock['bid'] = bid
    stock['ask'] = ask
    stock['days_range'] = days_range
    stock['week_range'] = week_range
    stock['volume'] = volume
    stock['avg_volume'] = avg_volume
    stock['market_cap'] = market_cap
    stock['beta'] = beta
    stock['pe_ratio'] = pe_ratio
    stock['eps'] = eps
    stock['earnings_date'] = earnings_date
    stock['dividend_yield'] = dividend_yield
    stock['ex_dividend_date'] = ex_dividend_date
    stock['year_target_est'] = year_target_est

    return stock

def main():
    st.title('Stock Scraper & Chatbot App')

    # Ticker symbols input
    ticker_symbols = st.text_input('Enter ticker symbols (separated by spaces):')

    if st.button('Scrape Stocks'):
        if ticker_symbols:
            options = Options()
            options.add_argument('--headless')

            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )

            driver.set_window_size(1150, 1000)

            stocks = []

            for ticker_symbol in ticker_symbols.split():
                stocks.append(scrape_stock(driver, ticker_symbol))

            driver.quit()

            csv_header = stocks[0].keys()

            with open('stocks.csv', 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, csv_header)
                dict_writer.writeheader()
                dict_writer.writerows(stocks)

            st.success('Stock data scraped and saved to stocks.csv')
        else:
            st.warning('Enter at least one ticker symbol.')

    # Check if stocks have been scraped and saved
    if os.path.exists('stocks.csv'):
        #st.success('Stock data scraped and saved to stocks.csv')

        # Set OPENAI_API_KEY
        os.environ["OPENAI_API_KEY"] = Apifile.API

        st.title("Chatbot")

        # Input field for user query
        query = st.text_input("Enter your query:")

        # Load the text document
        loader = TextLoader('stocks.csv')

        # Create an instance of ChatOpenAI
        chat_openai_instance = ChatOpenAI()

        # Create an index from the loader
        index = VectorstoreIndexCreator().from_loaders([loader])

        # Check if query is not empty
        if query:
            # Perform query and get the response
            response = index.query(query, chat_openai_instance)

            # Display the response
            st.write("Chatbot Response:")
            st.write(response)

if __name__ == '__main__':
    main()
