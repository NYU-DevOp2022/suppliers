$(function () {

    var BASE_URL = '/api';
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
            url: BASE_URL+"/suppliers",
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
                url: `${BASE_URL}/suppliers/${supplier_id}`,
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
            url: `${BASE_URL}/suppliers/${supplier_id}`,
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
            url: `${BASE_URL}/suppliers/${supplier_id}`,
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
            url: `${BASE_URL}/suppliers?${queryString}`,
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

    // ****************************************
    // Activate a Supplier
    // ****************************************

    $("#activate-btn").click(function () {

        let supplier_id = $("#supplier_id").val();

        supplier_id = parseInt(supplier_id);

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `${BASE_URL}/suppliers/${supplier_id}/active`,
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
    // Deactivate a Supplier
    // ****************************************

    $("#deactivate-btn").click(function () {

        let supplier_id = $("#supplier_id").val();

        supplier_id = parseInt(supplier_id);

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/suppliers/${supplier_id}/deactive`,
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
    // Item
    // ****************************************

    // Updates the form with data from the response
    function update_form_data_item(response) {
        $("#item_id").val(response.id);
        $("#item_name").val(response.name);
    }

    /// Clears all form fields
    function clear_form_data_item() {
        $("#item_name").val("");
    }

    // Updates the flash message area
    function flash_message_item(message) {
        $("#flash_message_item").empty();
        $("#flash_message_item").append(message);
    }

        // ****************************************
    // Create a Item
    // ****************************************

    $("#create-btn-item").click(function () {

        let name = $("#item_name").val();
        
        let data = {
            "name": name
        };

        $("#flash_message_item").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: BASE_URL+"/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(response){
            update_form_data_item(response)
            flash_message_item("Success")
        });

        ajax.fail(function(response){
            flash_message_item(response.responseJSON.message)
        });
    });


    // ****************************************
    // Delete a Item
    // ****************************************

    $("#delete-btn-item").click(function () {

        let item_id = $("#item_id").val();

        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(response){
            clear_form_data_item()
            flash_message_item("Item has been Deleted!")
        });

        ajax.fail(function(response){
            flash_message_item("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn-item").click(function () {
        $("#item_id").val("");
        $("#flash_message_item").empty();
        clear_form_data_item()
    });

    // ****************************************
    // Search for a Item
    // ****************************************

    $("#search-btn-item").click(function () {

        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(response){
            //alert(res.toSource())
            $("#search_results_item").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < response.length; i++) {
                let item = response[i];
                table +=  `<tr id="row_${i}"><td>${item.id}</td><td>${item.name}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results_item").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_form_data_item(firstItem)
            }

            flash_message_item("Success")
        });

        ajax.fail(function(response){
            flash_message_item(response.responseJSON.message)
        });
    });

    $("#show-btn").click(function () {

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(response){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Item</th>'
            table += '<th class="col-md-2"></th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < response.length; i++) {
                let item = response[i];
                table +=  `<tr id="row_${i}"><td id="item_id">${item.id}</td><td>${item.name}</td><td><button type="submit" id= "add-btn">Add</button></td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_form_data_item(firstItem)
            }

            flash_message_item("Success")
        });

        ajax.fail(function(response){
            flash_message_item(response.responseJSON.message)
        });
    });

    $("#list-item-btn").click(function () {

        let supplier_id = $("#supplier_id").val();

        supplier_id = parseInt(supplier_id);

        let data = {
            "supplier_id": supplier_id
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/suppliers/${supplier_id}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(response){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Item</th>'
            table += '<th class="col-md-2"></th>'           
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < response.length; i++) {
                let item = response[i];
                table +=  `<tr id="row_${i}"><td id="item_id">${item.id}</td><td>${item.name}</td><td><button type="submit" id= "remove-btn">delete</button></td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_form_data_item(firstItem)
            }

            flash_message_item("Success")
        });

        ajax.fail(function(response){
            flash_message_item(response.responseJSON.message)
        });
    });

    $(document).on('click', '#add-btn', function(){
        let item_id = $(this).parent().parent().find("td").eq(0).text();
        item_id = parseInt(item_id);
        let supplier_id = $("#supplier_id").val();
        supplier_id = parseInt(supplier_id);

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `${BASE_URL}/suppliers/${supplier_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            //alert(res.toSource())
            flash_message("Success")
        });

    });

    $(document).on('click', '#remove-btn', function(){
        let item_id = $(this).parent().parent().find("td").eq(0).text();
        item_id = parseInt(item_id);
        let supplier_id = $("#supplier_id").val();
        supplier_id = parseInt(supplier_id);

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/suppliers/${supplier_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        });

        $(this).parent().parent().remove();

        ajax.done(function(res){
            //alert(res.toSource())
            flash_message("Success")
        });

    });
})
