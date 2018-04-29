import sys
import datetime
import json
from time import mktime
from .utils import *
import argparse

class vulnSearchDate:

    def convertDate2Epoch(self, days, month, year, debug):
        self.debug = debug

        try:
            date_obj = datetime.date(int(year), int(month), int(days))
            timestamp = mktime(date_obj.timetuple())

        except Exception as e:
            if self.debug:
                print('Error: date info below')
                print(days, month, year)
                print(timestamp)
                print(datetime.datetime.fromtimestamp(timestamp))
                print()

            return e

        return timestamp

    def betweenDates(self, vulns, beginYear, endYear, debug):

        beginDay = 1
        beginMonth = 1
        endDay = 31
        endMonth = 12
        start = self.convertDate2Epoch(beginDay, beginMonth, beginYear, debug)
        end = self.convertDate2Epoch(endDay, endMonth, endYear, debug)
        out = {}

        if debug:
            print('\nStart Date: {}   End Date: {}'.format(start, end))
        temp = eval(json.dumps(vulns, default=lambda o: o.__dict__))
        for item in temp:
            if ( temp[item]["datePublic"] <= end and start <= temp[item]["dateLastUpdated"]):
                out[item] = temp[item]
                if debug:
                    print(str(temp[item]))

        return out


    def run(self, debug, vendor, product, searchMax, beginYear, endYear):
        vulns = Search().run(debug, vendor, product, searchMax)
        results = self.betweenDates(vulns, beginYear, endYear, debug)
        #out = ''

        #for item in results:
            #out = out + json.dumps(results[item], default=lambda o: o.__dict__)


        """for item in results:
            out = out + json.dumps(results[item], default=lambda o: o.__dict__)
            print(out)

        if debug:
            print("Total number of vulns scraped: {}\n".format(len(results)))
            print(out)

        return results
        """

        ## new code after taking results ##
        # print("Total number of vulns scraped: {}\n".format(len(results)))
        temp_Results = eval(json.dumps(results, default=lambda o: o.__dict__))
        finalresults = []
        for item in temp_Results:
            temp = {key: temp_Results[item][key] for key in temp_Results[item] if
                    key in ["datePublic", "dateLastUpdated", "vulnID", "severityMetric", "search_url"]}    #creating a dictionary using data scraped from the database
            finalresults.append(temp)
        return finalresults
        ## end of new code##

## new code ##
def check_overlap(dategroup, date):                 #checking for the overlap from vendor1 and vendor2
    overlapps = []
    for everydate in dategroup:
        if int(date[0]) <= int(everydate[1]) and int(everydate[0]) <= int(date[1]):
            temp = sorted([int(date[0]), int(date[1]), int(everydate[0]), int(everydate[1])])
            overlapps.append([temp[1], temp[2], everydate[2], everydate[3], everydate[4]])
    return overlapps

def get_combined(row, overlaps):                    #if an overlap is found from the two vendors displaying in the third timeline
    extemp = {key: val for key, val in row.items()}
    tempseverities = []
    temp = []
    if overlaps:
        for overlap in overlaps:
            tempseverities.append([{overlap[2]:overlap[4], extemp["vulnID"]:extemp["search_url"]},
                                   float('%.3f' % ((float(row["severityMetric"]) + float(overlap[3])) / 2))])    #calculating the average of severity metrics
            combined = {key: val for key, val in row.items()}
            combined["start"] = overlap[0]
            combined["end"] = overlap[1]
            combined["id"] = overlap[2] + '-' + extemp["vulnID"] if float(combined["severityMetric"]) >= 5.0 else " "
            combined["lane"] = 2
            temp.append(combined)
    return temp, tempseverities

def compute(results):
    count = 0
    final = []
    severities = []
    ven1_dates = []
    combined_severities = []
    for vendor in results:
        temp = []
        for row in vendor:
            if row["datePublic"] == row["dateLastUpdated"]:
                startdate = datetime.datetime.fromtimestamp(
                    int(row["datePublic"]))
                enddate = startdate + datetime.timedelta(days=10)      #id datePubllic is same as dateLastUpdated adding 10days to the starting date
                row["dateLastUpdated"] = enddate.timestamp()
            if count == 0:
                ven1_dates.append([row["datePublic"], row["dateLastUpdated"], row["vulnID"], row["severityMetric"], row["search_url"]])
            else:
                overlaps = check_overlap(ven1_dates, [row["datePublic"], row["dateLastUpdated"]])
                combined, temp_sever = get_combined(row.copy(), overlaps)
                if combined:
                    final.extend(combined)
                    combined_severities.extend(temp_sever)
            temp.append([row["vulnID"], float(row["severityMetric"]), row["search_url"]])
            row["start"] = row["datePublic"]
            row["end"] = row["dateLastUpdated"]
            row["id"] = row["vulnID"]
            row["lane"] = count
            del row["datePublic"]
            del row["dateLastUpdated"]
            del row["vulnID"]
            final.append(row)
        count += 1
        try:
            temp.sort(key=lambda t: t[1], reverse=True)
        except TypeError:
            pass
        severities.append(temp)
    if combined_severities:
        combined_severities.sort(key=lambda t: t[1], reverse=True)

    return final, severities, combined_severities

    ## end of new code##


"""if __name__ == "__main__":
    #Parsing the command line for arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='turn on script debugging', action='store_true', default=False)
    parser.add_argument('vendor', help='Vendor of product',type=str)
    parser.add_argument('product', help='Product to search for',type=str)
    parser.add_argument('searchMax', help='Input number of results to return. Default is all', nargs='?', type=str, default='all')
    parser.add_argument('beginYear', help='input year to start search',type=int)
    parser.add_argument('endYear', help='input year to end search',type=int)

    args = parser.parse_args()

    vulnSearchDate().run(args.debug, args.vendor, args.product, args.searchMax, args.beginYear, args.endYear)
"""
