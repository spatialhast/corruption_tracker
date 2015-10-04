function main_map_init (map, options) {
    // Add GeoJSON layer   
    var marker, org_row, orgs_set, org_rows;

    // Add building markers with popups to buildings.
    for (var i = buildings['features'].length - 1; i >= 0; i--) {

        var myIcon = L.divIcon({
            className: 'icon_with_number',
            html: buildings['features'][i]['properties']["polygon_claims"]
        }); 

        marker = L.marker(
            [
                buildings['features'][i]['properties']["centroid"][1],
                buildings['features'][i]['properties']["centroid"][0],
            ],
            {icon: myIcon}
        )

        orgs_set = buildings['features'][i]['properties']["organizations"]
        var polygon = L.polygon(buildings['features'][i]["geometry"]["coordinates"]);

        org_rows = []
        for (var ii = orgs_set.length - 1; ii >= 0; ii--) {
            org_row = document.createElement('a');
            org_row.href = "#";
            org_row.id = orgs_set[ii]['id'];
            org_row.innerHTML = orgs_set[ii]['name'] + ': &nbsp;&nbsp;' + orgs_set[ii]['claims_count'];

            org_id = orgs_set[ii]['id'];

            org_row.onclick = function(event) {
                select_building($(this).attr('id'));  
                // Here have to be implemented zoom on selected organization       
                // map.setView(buildings['config']['center'], buildings['config']['zoom']);
                event.preventDefault();
                };
            org_rows.push(org_row);
            }; 

            // Here have to be implemented callback for polygon with single org
            // if (orgs_set.length == 1){                
            //     polygon.onclick = function(event) {
            //         console.log('polygon clicked');
            //         select_building(org_row.id);
            //     }   
            // }

        org_list = document.createElement("ul");
        $.each(org_rows, function(i)
        {
            var li = $('<li/>')
                .addClass('ui-menu-item')
                .attr('role', 'menuitem')
                .appendTo(org_list);        
            li.html(org_rows[i]);  
        });
        marker.addTo(map);
        polygon.addTo(map).bindPopup(org_list);
    };
    // L.geoJson(buildings).addTo(map);
    map.setView(buildings['config']['center'], buildings['config']['zoom']);
  
}