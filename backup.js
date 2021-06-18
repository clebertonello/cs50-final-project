/* source= https://stackoverflow.com/questions/1801499/how-to-change-options-of-select-with-jquery */
$(function() {
    $('#purchases').on('change', function() {

        $.getJSON($SCRIPT_ROOT + '/fetchsubcat', {
            query_sub: $('select[name="purchases"]').val(),
        },
            function(data) {

                var newOptions = data.sublist;
                var supAc = data.supplierlist

                var supplier_array = $.map(supAc, function(value, index){return [value[0]];});

                console.log(supplier_array);

                document.getElementById("teste").innerHTML = typeof(data.supplierlist)

                var $el = $("#subcat");
                $el.empty(); // remove old options
                $.each(newOptions, function(key,value) {
                $el.append($("<option></option>")
                    .attr("value", value[0]).text(value[1]));                    
                });

                $("#supplier").autocomplete({
                    source: supplier_array,
                    minLength: 1
                })
            });
    });
});


$('.show').click(function() {
    $.getJSON($SCRIPT_ROOT + '/fetchpur',{
        query: $(this).val(),
    },function(data) {
        console.log(data.purlist);
        console.log(data.q);
        $('#' + data.q).empty();
        var content = "<thead><tr style='text-align:center'><th scope='col'>Item</th><th scope='col'>Quantity</th><th scope='col'>Unit Price</th><th scope='col'>Total</th><th scope='col'>Supplier</th></tr></thead><tbody>";
        for(var i = 0; i < data.purlist.length; i++){
            content += "<tr style='text-align:center'>"
            content += "<td>" + data.purlist[i].produto_nome + "</td>"
            content += "<td>" + data.purlist[i].quant + "</td>"
            content += "<td>" + data.purlist[i].preco_unit + "</td>"
            content += "<td>" + data.purlist[i].total + "</td>"
            content += "<td>" + data.purlist[i].fornecedor_nome + "</td>"
            content += "</tr>"
        }
        content += "</tbody>"                   
        $('#' + data.q).append(content);        
    })

});

$('.show').click(function () {
    var q = $(this).val()
    $.getJSON($SCRIPT_ROOT + '/fetchsubcat', {
        query: q,
    }, function (data) {
        $(".dyntable").empty();
        var content = "<tr class=' dyntable'><td colspan='6'><table style='padding: 15px' class='table table-secondary align-middle'>\
            <thead>\
                <tr style='text-align:center'>\
                    <th scope='col' width='20%'>ID</th>\
                    <th scope='col' width='50%'>SubCat</th>\
                    <th scope='col' width='15%'></th>\
                    <th scope='col' width='15%'></th>\
                </tr>\
            </thead>\
            <tbody>";

        for (var i = 0; i < data.sublist.length; i++) {
            content += "<tr style='text-align:center' id='removeLine'><form action='/category' method='POST' id='removeTarget'>"
            content += "<td>" + data.sublist[i].id + "<input type='hidden' value=" + data.sublist[i].id + "></td>"
            content += "<td style='text-transform:capitalize;'>" + data.sublist[i].descricao + "</td>"
            content += "<td></td>"
            content += "<td><button class='btn btn-secondary subremove' type='button' name='postbutton' value='remove'>Remove</button></td>"
            content += "</form></tr>"
        }
        content += "</tbody></table></tr>"
        /* $(content).insertAfter($('#tr' + q)); */
        $('#tr' + q).append($(content));
    })
});