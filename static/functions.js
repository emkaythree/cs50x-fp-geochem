function searchtype()
{
    var type = document.getElementById("type").value;

    if (type == "solution_master_species") {
        document.getElementById("SMS_search").hidden = false;
        document.getElementById("SS_search").hidden = true;
        document.getElementById("PH_search").hidden = true;
    }
    else if (type == "solution_species") {
        document.getElementById("SMS_search").hidden = true;
        document.getElementById("SS_search").hidden = false;
        document.getElementById("PH_search").hidden = true;
    }
    else if (type == "phases") {
        document.getElementById("SMS_search").hidden = true;
        document.getElementById("SS_search").hidden = true;
        document.getElementById("PH_search").hidden = false;
    }
    else {
        document.getElementById("SMS_search").hidden = true;
        document.getElementById("SS_search").hidden = true;
        document.getElementById("PH_search").hidden = true;
    }

}