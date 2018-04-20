from django.shortcuts import render
from .utils import Search, compute
# Create your views here.
def index(request):
    vendorlist = {"Cisco": "Anyconnect",
                  "Juniper" : "VPN",
                  "OpenVPN" : "VPN",
                  "F5": "VPN"
                  }
    if request.method == "POST":
        vendor1 = request.POST.get("layer1")
        vendor2 = request.POST.get("layer2")
        lane = 0
        vendors = [vendor1, vendor2]
        results = []
        for vendor in vendors:
            results.append(Search().run("-d", vendor, vendorlist[vendor], 50))

        data = compute(results)

        return render(request, 'index.html', {"vendorlist": vendorlist.keys(), "data":data})
    else:
        return render(request, 'index.html',{"vendorlist":vendorlist.keys()})

