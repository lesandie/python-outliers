import click
from csv import DictReader, DictWriter
from datetime import datetime
from app.loadmonth import *
from app.functions import *

@click.command()
@click.option("--input", required=True, type=str, help="Input CSV filename for parsing")
@click.option("--output", required=True, type=str, help="Output CSV filename for writing")

def main(input: str, output: str):
    """
    Basic parsing utility
    """    
    
    # Set logging level
    logging.basicConfig(level=logging.INFO, filename='parsing.log', filemode='w',format='%(asctime)s - %(levelname)s - %(message)s')
    # check_input_parameters returns True or False if all the params are correct
    if check_filepath(input) is not False:
        with open(input, mode="r", encoding="utf-8-sig", newline="\n") as fhandler, \
                    open(output, mode="w", encoding="utf-8-sig", newline="\n") as fhandlew:
            #Init load_month objects in a dict
            loader = {
                'Sep.21': LoadMonth('Sep.21'),  
                'Oct.21': LoadMonth('Oct.21'),
                'Nov.21': LoadMonth('Nov.21'),
                'Dec.21': LoadMonth('Dec.21'),
                'Jan.22': LoadMonth('Jan.22'),
                'Feb.22': LoadMonth('Feb.22'),
            }
            # init last current date and z_score
            current_date = datetime(1970,1,1,0,0)
            z_score = None
            # if not provided in the constructor, at least one row has to be retrieved before getting the fieldnames.
            areader = DictReader(fhandler, delimiter=",")
            #now we have the fieldnames/header to be written in the output file
            awriter = DictWriter(fhandlew, areader.fieldnames)
            awriter.writeheader()
            #begin the readline process and calculus
            for row in areader:
                #read line
                date_item = check_datetime(row['generated_on'])
                value = float(row['dlvd_price'])
                if date_item >= current_date and date_item is not None:
                    try:
                        current_date = date_item
                        # process rows normally
                        # TODO key exception for loader dict
                        z_score = process_csv_row(date_item, value, loader[row['load_month']])
                    except Exception as e:
                        raise KeyError('Load Month is not in the expected list')
                elif date_item < current_date and date_item is not None:
                    # process anomalous order value
                    try:
                        z_score = order_insert(date_item, value, loader[row['load_month']])
                    
                    except Exception as e:
                        raise KeyError('Load Month is not in the expected list')                
                else:
                    logging.error(f"Current date is None ---> {current_date}")
                
                #Now checking for outliers if not write to file. If z_score is None the date is wrong
                if z_score >= 1.95 or z_score <= -1.95:
                    logging.info('------------------------------------------------------------------------------------------------------------')
                    logging.info(f'''Outlier detected for date {date_item.strftime('%Y-%m-%d %H:%M:%S')}: Window: {loader[row['load_month']].window_get()} value={value} and zscore={z_score}''')
                else:
                    #Change the string format to another
                    row['generated_on'] = date_item.strftime('%Y-%m-%d %H:%M:%S')
                    awriter.writerow(row)
        #plot graph
        plot_graph(**loader)
        
if __name__ == '__main__':
    main()
