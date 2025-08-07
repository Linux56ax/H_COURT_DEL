from bs4 import BeautifulSoup

def extract_case_info(html_content):
    """
    Parses an HTML table to extract case order dates and their corresponding links.

    Args:
        html_content (str): The HTML content containing the table.

    Returns:
        list: A list of dictionaries, where each dictionary contains the 'date'
              and 'link' for a specific case order.
    """
    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table by its ID and then the tbody section
    table = soup.find('table', id='caseTable')
    if not table:
        print("Table with id='caseTable' not found.")
        return []

    tbody = table.find('tbody')
    if not tbody:
        print("Table body (tbody) not found.")
        return []

    results = []
    # Iterate through each row (tr) in the table body
    for row in tbody.find_all('tr'):
        # Find all the data cells (td) in the current row
        cells = row.find_all('td')

        # Ensure the row has enough columns to avoid index errors
        if len(cells) >= 3:
            # The date is in the third column (index 2)
            date_of_order = cells[2].text.strip()

            # The link is in the second column (index 1), inside an anchor tag (<a>)
            link_tag = cells[1].find('a')
            if link_tag and 'href' in link_tag.attrs:
                order_link = link_tag['href']
                
                # Append the extracted data to our results list
                results.append({
                    'date': date_of_order,
                    'link': order_link
                })
    
    return results

#data input html 
html_data= """[<table aria-describedby="caseTable_info" class="table table-hover table-bordered text-center dataTable" id="caseTable" style="width: 100%;"><colgroup><col data-dt-column="0" style="width: 95.9062px;"/><col data-dt-column="1" style="width: 227.922px;"/><col data-dt-column="2" style="width: 173.125px;"/><col data-dt-column="3" style="width: 306.391px;"/><col data-dt-column="4" style="width: 175.656px;"/></colgroup>
<thead>
<tr role="row"><th aria-label="S.No." aria-sort="ascending" class="dt-orderable-none dt-ordering-asc" colspan="1" data-dt-column="0" rowspan="1"><span class="dt-column-title">S.No.</span><span class="dt-column-order"></span></th><th aria-label="Case No/Order Link.: Activate to sort" class="dt-orderable-asc dt-orderable-desc" colspan="1" data-dt-column="1" rowspan="1" tabindex="0"><span class="dt-column-title" role="button">Case No/Order Link.</span><span class="dt-column-order"></span></th><th aria-label="Date of Order: Activate to sort" class="dt-orderable-asc dt-orderable-desc" colspan="1" data-dt-column="2" rowspan="1" tabindex="0"><span class="dt-column-title" role="button">Date of Order</span><span class="dt-column-order"></span></th><th aria-label="Corrigendum Link/Corr. Date: Activate to sort" class="dt-orderable-asc dt-orderable-desc" colspan="1" data-dt-column="3" rowspan="1" tabindex="0"><span class="dt-column-title" role="button">Corrigendum Link/Corr. Date</span><span class="dt-column-order"></span></th><th aria-label="HINDI ORDER: Activate to sort" class="dt-orderable-asc dt-orderable-desc" colspan="1" data-dt-column="4" rowspan="1" tabindex="0"><span class="dt-column-title" role="button">HINDI ORDER</span><span class="dt-column-order"></span></th></tr>
</thead>
<tbody><tr><td class="sorting_1">1</td><td><a href="https://delhihighcourt.nic.in/app/showlogo/1751968422_c62e49412dc3326f_680_12012025.pdf/2025" target="_blank">BAIL APPLN. 1201/2025</a></td><td>04/07/2025</td><td></td><td></td></tr><tr><td class="sorting_1">2</td><td><a href="https://delhihighcourt.nic.in/app/showlogo/100025561743084247605_26049_12012025.pdf/2025" target="_blank">BAIL APPLN. 1201/2025</a></td><td>27/03/2025</td><td></td><td></td></tr></tbody>
<tfoot></tfoot></table>]"""


#Function call
case_details = extract_case_info(html_data)

#Result print
for case in case_details:
    print(f"Date: {case['date']}, Link: {case['link']}")