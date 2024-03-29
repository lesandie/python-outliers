
# Detect and plot outliers using Python

## Data Exercise

The goal of this exercise is to implement a script that reads the csv document provided, analyze, and clean the data from outliers.

The document provided has all the calculated values to gather the delivery price of gasoline in the ARA (Europe) to NY route, called RBOB, for 6 different months. The document contains one work week of data.

The important columns of the ```RBOB_data_test``` are:

- generated_on: This column contains the date of the calculation of the data, usually we make a calculation per route/month every 15 minutes, but this can not be allways true due to a changes of some prices or errors on the backend.
- display_name: This columns contains the name of the route, in this document we have only included RBOB, that is the route we need to analyse.
- load_month: This column contain the month for the one we are calculating the prices. Currently we calculate the current month, and 5 in the future. This document that was generated at the end of September you will be able to see calculations for Sep'21, Oct'21, Nov'21, Dec'21, Jan'22, Feb'22.
- dlvd_price: The final price of delivery, the value we need to analyse and clean.

After being able to read and plot the data, in a meeting with the stakeholders, they have marked which are the clear outliers in the data, and ask you to being able to detect them in real time, and remove them before are sent to the backend to plot the historics.

![plotted data for the text](https://i.imgur.com/1Mzc1bU.png)

## The work to be done for this exercise is:

1. Create a script that can read the data sequentially, and solve any format problems that could appear.
2. Plot the data to find the outliers
3. Iterate the read script to detect the outliers and save the data cleaned in a separated csv.

To give your answer, create a repository in any platform you feel conformable with and share it with us. Over that solution we will discuss in a pair-programming about the solution chosen, the thoughts to reach that solution, and a possible improvement.

## The problem

Basically to detect outliers it is advisable to begin with a simple exploratory analysis of the dataset, using a Jupyter notebook and Pandas, but I went directly to
check the CSV and the coding session helped me to detect the outliers and the formatting problems. One of the problems was that the CSV is coded with BOM format and
had to be taken into account opening the file with ```utf-8-sig``` property. Also the ```generated_on``` column has different formats (```21.09.21 12:12``` and ```2021-12-09 12:34:23.087```) and had to be taken into account too. These formatting problems are usually detected during the exploratory analysis.

Once this formatting problems were solved, I used a zscore to get the outliers. Localities (values in near windows of time tend to have a low std) are very common calculating avgs and stds for streamed/continuous data so it is advisable, statistically speaking, to select a time frame/window (last 45 min in our case) and use the values of that window to calculate the zscore for the current value. 

Also another important issue is to begin with an acceptable range for the zscore, being +2 and -2 a good baseline, that actually works nicely in this dataset, because the outliers are very clear. In order to test the zscore range for this dataset, I've generated a ```test_values.txt``` to use it as a guide and validate the z-score calculations.

And last, but not least is that some calculations are sent (as described in the test above) async. I've changed from a list to a dict to order the timeseries and plot the calculations althought the're arriving later that expected.

## Solution proposed

I could use asyncio and aiocsv to process asynchronously all the basic IO from and to files but I tried to keep it simple.

Create a pyenv virtualenv (I've update the code from 3.8 to 3.11.0 and configured a pyproject to generate a package) and execute the script as follows:

```bash
(dev) ➜ git:(main) ✗ pip install -e .
(dev) ➜ git:(main) ✗ plot-cli --help
Usage: plot-cli [OPTIONS]

  Basic parsing and plotting utility

Options:
  --input TEXT   Input CSV filename for parsing  [required]
  --output TEXT  Output CSV filename for writing  [required]
  --help         Show this message and exit.
```

Simply specify the filename to read from:

```bash
(dev) ➜ git:(main) ✗ plot-cli --input RBOB_data_test.csv --output cleaned_RBOB_data.csv
```

The script will:
- generate a detailed log ```parsing.log``` with the outliers and the error dates. 
- fix timestamp formatting problems.
- write the cleaned data to a file named ```cleaned_RBOB_data.csv``` with the original header.
- plot the graphs in the same figure.

## Future WIP

The best way to obtain an ordered CSV (because there are out-of-order events arriving later) is to load chunks of the cleaned file into PostgreSQL and generate an ordered CSV using ```COPY``` and ```FORMAT``` commands. This way we can have a second copy of the csv in a database and we can use the benefits of an ORDER BY SELECT to order the results and write them to a CSV file. This could be done with a UDF in ```PL/pgSQL``` and an ```unlogged``` table to speedup the insertion process.
Why adding a Database?. Because of scalability, if the file is so big, no python script can manage in RAM, then it is better to ingest into a database and use it to sort data.
