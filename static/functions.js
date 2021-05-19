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

function showdelete(x)
{
    var row = document.getElementsByClassName("deletedb");
    row[x-1].style.visibility = "visible";
}

function hidedelete(x)
{
    var row = document.getElementsByClassName("deletedb");
    row[x-1].style.visibility = "hidden";
}
