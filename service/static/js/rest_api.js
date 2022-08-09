$(function () {


    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#supplier_id").val(res.id);
        $("#supplier_name").val(res.name);
        if (res.available == true) {
            $("#supplier_available").val("true");
        } else {
            $("#supplier_available").val("false");
        }
        $("#supplier_address").val(res.address);
        $("#supplier_rating").val(res.rating);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#supplier_name").val("");
        $("#supplier_available").val("");
        $("#supplier_address").val("");
        $("#supplier_rating").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Supplier
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#supplier_name").val();
        let available = $("#supplier_available").val() == "true";
        let address = $("#supplier_address").val();
        let rating = $("#supplier_rating").val();

        rating = parseFloat(rating);
        rating.toFixed(2);




        let data = {
            "name": name,
            "available": available,
            "address": address,
            "rating": rating
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/suppliers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Supplier
    // ****************************************

    $("#update-btn").click(function () {

        let supplier_id = $("#supplier_id").val();
        let name = $("#supplier_name").val();
        let available = $("#supplier_available").val() == "true";
        let address = $("#supplier_address").val();
        let rating = $("#supplier_rating").val();

        rating = parseFloat(rating);
        rating.toFixed(2);


        let data = {
            "name": name,
            "available": available,
            "address": address,
            "rating": rating
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/suppliers/${supplier_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Supplier
    // ****************************************

    $("#retrieve-btn").click(function () {

        let supplier_id = $("#supplier_id").val();

        supplier_id = parseInt(supplier_id);

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/suppliers/${supplier_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Supplier
    // ****************************************

    $("#delete-btn").click(function () {

        let supplier_id = $("#supplier_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/suppliers/${supplier_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Supplier has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#supplier_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Supplier
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#supplier_name").val();
        let available = $("#supplier_available").val() == "true";
        let address = $("#supplier_address").val();

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }
        if (address){
            queryString += 'address=' + address
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/suppliers?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '<th class="col-md-2">Rating</th>'
            table += '</tr></thead><tbody>'
            let firstSupplier = "";
            for(let i = 0; i < res.length; i++) {
                let supplier = res[i];
                table +=  `<tr id="row_${i}"><td>${supplier.id}</td><td>${supplier.name}</td><td>${supplier.available}</td><td>${supplier.address}</td><td>${supplier.rating}</td></tr>`;
                if (i == 0) {
                    firstSupplier = supplier;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstSupplier != "") {
                update_form_data(firstSupplier)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
