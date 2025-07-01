import pandas as pd
import chardet
import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
import time
import datetime
import numpy as np
import concurrent.futures

# Load older congressional bills and drop rows missing "Minor" category
bills93 = pd.read_csv("datasets_topic/bills93-114.csv", encoding="latin1")
bills93 = bills93.dropna(subset=['Minor'])
bills93 = bills93.reset_index(drop=True)

# Create a unique BillID for each bill
unique_bill_types = pd.unique(bills93["BillType"])
for index, row in bills93.iterrows():
    bills93.at[index, "BillID"] = str(bills93.at[index, "Cong"]) + "-"+ str(bills93.at[index, "BillType"]) +"-"+ str(bills93.at[index, "BillNum"]) 

# Load newer bills and standardize column names
bills115 = pd.read_csv("datasets_topic/bills115-116.csv")
bills115 = bills115[["BillID", "BillNum", "BillType", "Chamber", "congress", "Cosponsr", "Title", "Major", "Minor", "nominate_dim1"]].rename(columns = {'congress': 'Cong'})
bills115.dropna(inplace=True)

# Combine both datasets into one
combined = pd.concat([bills93, bills115], ignore_index=True)

# Rebuild BillID with standard format: <congress>-<billTypeInitial>-<billNum>
for index, row in combined.iterrows():
    combined.at[index, "BillID"] = str(combined.at[index, "Cong"]) + "-"+ str(combined.at[index, "BillType"][0]) +"-"+ str(combined.at[index, "BillNum"]) 

# Load roll call voting data and combine detail and text in one column
df_stance = pd.read_csv("dataset_nomiate/HSall_rollcalls.csv")
df_stance["title"] = df_stance["dtl_desc"].fillna("")+ " "+ df_stance["vote_desc"].fillna("")

# Keep only necessary columns and filter out early congresses
df_stance = df_stance[["congress","chamber","bill_number","title" ,"nominate_mid_1","nominate_mid_2"]]
df_stance.dropna(inplace=True)
df_stance = df_stance[df_stance["congress"]>93]

# Parse bill_number to extract standard bill type and number for ID creation
cat_hash = set()
num_of = {'H': 0,'HCON': 0,'HCONR': 0,'HCONRES': 0,'HCR': 0,'HCRES': 0,'HHR': 0,'HJ': 0,'HJR': 0,'HJRES': 0,'HR': 0,'HRE': 0,'HRES': 0,'HRJ': 0,'HT': 0,'S': 0,'SCON': 0,'SCONR': 0,'SCONRES': 0,'SCR': 0,'SJ': 0,'SJR': 0,'SJRES': 0,'SRE': 0,'SRES':0}
for i in range(len(df_stance)):
    text = df_stance.at[i, "bill_number"]

    if isinstance(text, str):
        result = re.findall(r'[A-Za-z]+|\d+', text)
        if(result[0]=='HR' or result[0]=='S' or result[0]=='HJRES'or result[0]=='SJRES' ):
            cat_hash.add(result[0])
            num_of[result[0]]+=1
            df_stance.at[i, "billID"] = str(df_stance.at[i, "congress"]) + "-" + str(result[0][0].lower()) + "-"+ str(result[1])
        else:
            # Drop rows with bill types outside the ones of interest
            df_stance.drop(i, inplace=True)
    else:
        result = [] 
        print("error")

# Final cleanup before processing
df_stance.dropna(subset=["title", "nominate_mid_1", "bill_number"], inplace= True)
df_stance.drop(['index', 'level_0'], axis=1, inplace=True)
df_stance.reset_index(inplace =True)

no_sum = []
errors = []

# Clean the raw HTML and remove tags from the text
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ").strip()

# Builds a bill's full summary text  if not available, uses title instead
def procces_bill(billID):
    cong, chamber, bill = re.findall(r'[A-Za-z]+|\d+', billID)
    if chamber == "h":
        chamber = "hr"
    else:
        chamber = "s"

    text, is_sum = fetch_summary(bill, cong, chamber)

    if not is_sum:
        no_sum.append(billID)
        text = fetch_title(bill, cong, chamber)

    return (billID, text)   

# Try to fetch bill summary from API 
def fetch_summary(bill_num, cong, chamber):
    retries = 3  # Set a limit on the number of retries
    retry_delay = 120  # Time to wait between retries (in seconds)
    
    while retries > 0:
        try:
            response = requests.get(f"{base_url}/bill/{cong}/{chamber}/{bill_num}/summaries?api_key={key}")
            response.raise_for_status()

            if response.status_code == 429:
                print(f"Rate limit hit. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retries -= 1
                continue

            summaries = response.json().get('summaries', [])
            if summaries:
                return summaries[-1]["text"], True
            return None, False

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            errors.append(f"{cong}-{chamber}-{bill_num}")
            return None, False
    
    print(f"Max retries reached for {cong}-{chamber}-{bill_num}. Skipping...")
    return None, False

# Fallback if no summary is found, use title of the bill instead
def fetch_title(bill_num, cong, chamber):
    retries = 3
    retry_delay = 120
    
    while retries > 0:
        try:
            response = requests.get(f"{base_url}/bill/{cong}/{chamber}/{bill_num}?api_key={key}")
            if response.status_code == 429:
                print(f"Rate limit hit. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retries -= 1
                continue

            json_bill = response.json()
            return json_bill['bill']['title']
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            errors.append(f"{cong}-{chamber}-{bill_num}")
            return None
    
    print(f"Max retries reached for {cong}-{chamber}-{bill_num}. Skipping...")
    return None

# Run summary/title fetching in parallel 
def process_bill_parallel(df):
    i = 0
    updates = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_bill = {executor.submit(procces_bill, row.billID): row for row in df.itertuples()}

        for future in concurrent.futures.as_completed(future_to_bill):
            i += 1
            billID, text = future.result()
            updates.append((billID, text))
            
    for billID, text in updates:
        df.loc[df['billID'] == billID, 'text'] = text

    # Save processed data and log status
    df.to_csv("curr_data_test.csv", index=False)
    with open("status_test.txt", 'w') as file:
        file.write(f"Errors: {errors} \n No_Sums: {no_sum}")
