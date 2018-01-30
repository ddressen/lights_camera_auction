
chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
    var url = tabs[0].url;
    console.log(url);
    
    //Extract ebay item id if on ebay, nothing otherwise
    var regExp = /^(?:https?:\/\/)?(?:www\.)?ebay\.com\/itm\/.*?\/(\d+)/i;
var match = url.match(regExp);
    if (match && match[1].length == 12) {
      document.getElementById("itemID").innerHTML = match[1];
    } else {
      document.getElementById("itemID").innerHTML = 'NONE DETECTED';//error
    }
});



document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('checkPage').addEventListener('click', function(){
      chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
        
        //get current url
    var url = tabs[0].url;

    //Extract ebay item id if on ebay, nothing otherwise
    var regExp = /^(?:https?:\/\/)?(?:www\.)?ebay\.com\/itm\/.*?\/(\d+)/i;
var match = url.match(regExp);
    if (match && match[1].length == 12) {
      var newURL = "http://127.0.0.1:5000/output?item_ID=" + match[1];
         chrome.tabs.create({ url: newURL });
    } else {
    }
    
    
         
      });
});
});