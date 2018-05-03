from django.shortcuts import render
import datetime
from .vulnSearchDate import vulnSearchDate, compute
# Create your views here.
def index(request):
    today = str(datetime.date.today())
    curr_year = int(today[:4])+1
    vendorlist = ["Cisco Anyconnect","Juniper VPN", "OpenVPN VPN"]
    vendors = ["vendor1", "vendor2", "Attack Window"]
    if request.method == "POST":
        vendor1 = request.POST.get("layer1")      #post request to Vendor1
        vendor2 = request.POST.get("layer2")      #POST request to vendor2
        StartYear = request.POST.get("StartDate")
        EndYear = request.POST.get("EndDate")
        print(vendor1, vendor2, StartYear, EndYear)
        c = 0
        vendors = [vendor1, vendor2]
        results = []
        for item in vendors:
            vendor, product = item.split(" ")
            print(vendor, product)
            results.append(vulnSearchDate().run("", vendor, product, 'all', StartYear, EndYear))

        data, severities, combined_severities = compute(results)           #computing the results importing from vlunSearchDate
        vendors.append("Attack Window")
        final_severities= {}
        for ven in severities:
            final_severities[vendors[c]] = ven
            c += 1
        print(combined_severities)
        return render(request, 'severity.html', {"vendorlist": vendorlist, "data":data, "vendors": vendors, "severities":final_severities, "Years":range(2000,curr_year), "combined_severities":combined_severities})
    else:
        return render(request, 'index.html',{"vendorlist":vendorlist, "vendors": vendors , "Years":range(2000,curr_year)})

def helpPage(request):
    return render(request, 'help.html')
