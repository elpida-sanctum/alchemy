$(document).ready(function () {
    var t = new Tabulator("#apn_table", {
        height: "400px",
        layout: "fitColumns",
        placeholder: "No Data",
        rowFormatter: function (row) {
            if (row.getData().status == "Added") {
                row.getElement().classList.add("table-success")
            } else if (row.getData().status == "Exists") {
                row.getElement().classList.add("table-danger")
            }
        },
        columns: [
            { title: "ID", field: "id", formatter: "rownum" },
            { title: "APN", field: "apn", sorter: "string", width: 200 },
            { title: "IP", field: "ip", sorter: "string", width: 100 },
            { title: "Route", field: "route", sorter: "string", width: 200 },
            { title: "Status", field: "status", sorter: "string", width: 200 },
            { formatter: "buttonCross", width: 40, hozAlign: "center", cellClick: function (e, cell) { cell.getRow().delete() } }
        ]
    });

    $('#addRow').on('click', function () {
        var send = JSON.stringify({ 'apn': $('#apn').val(), 'ip': $('#ip').val(), 'route': $('#route').val() })
        fetch('/api/validate', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                Connection: "close",
                Origin: "/api/validate",
            },
            body: send,
        }).then(function (response) {
            resp = response.json();
            return resp;
        }).then(function (data) {
            var button = '<button type="button" class="btn btn-danger btn-xs dt-delete">Delete</button>'
            pdata = JSON.parse(JSON.stringify(data))
            var result = {}
            var validity = {}
            $.each(pdata, function (key, val) {
                console.log(key + ": " + val.valid + "; " + val.value);
                if (val.valid) {
                    $("#" + key).removeClass('is-invalid');
                    $("#" + key).addClass('is-valid');
                    result[key] = val.value;
                    validity[key] = true;
                } else {
                    $("#" + key + "-tooltip").text();
                    $("#" + key).removeClass('is-valid');
                    $("#" + key).addClass('is-invalid');
                    $("#error-tooltip").text("Invalid data in field " + key);
                    validity[key] = false;
                }
            });
            console.log(validity);
            console.log(result);
            var all_valid = true;
            $.each(validity, function (key, value) {
                all_valid = all_valid && value;
            });
            console.log(all_valid);
            if (all_valid) {
                t.addRow({ apn: result['apn'], ip: result['ip'], route: result['route'], status: "New" })
                //t.row.add([result['apn'], result['ip'], result['route'], button]);
                //t.draw()
                //$('.dt-delete').off('click');
                //$('.dt-delete').each(function () {
                //    $("#data-table tbody").on('click', '.dt-delete', function (evt) {
                //        therow = $(this);
                //        var dtRow = therow.parents('tr');
                //        var indRow = t.row(dtRow).index();
                //        if (confirm("Are you sure to delete this row?")) {
                //            t.row(indRow).remove().draw(false);
            }
        });
        //});
    });

    $('#sendTable').on('click', function () {
        var dataT = t.getData();
        console.log(dataT);
        fetch('/api/add_apn', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                Connection: "close",
                Origin: "/api/add_apn",
            },
            body: JSON.stringify({ dataT }),
        }).then(function (response) {
            resp = response.json();
            return resp;
        }).then(function (id) {
            console.log(id);
            $.each(id, function (key, value) {
                console.log(value);
                t.getRows().forEach(row => {
                    var num = Number(row.getPosition()) - 1;
                    if (value && key == num) {
                        row.update({ status: "Added" });
                        row.reformat();
                    } else if (!value && key == num) {
                        row.update({ status: "Exists" });
                        row.reformat();
                    };
                });
                //var num = Number(key)
                //var row = t.getRow(num + 1);
                //row.reformat()
            });
        });
    });

    $("#uploadFile").on('click', function () {
        var file = $('#inputFile').prop('files')[0];
        var send = new FormData();
        send.append('file', file)
        fetch('/api/upload', {
            method: "POST",
            body: send,
        }).then(function (response) {
            resp = response.json();
            return resp;
        }).then(function (data) {
            $('#upload')[0].reset();
            console.log(data);
            var button = '<button type="button" class="btn btn-danger btn-xs dt-delete">Delete</button>'
            pdata = JSON.parse(JSON.stringify(data))
            $.each(pdata, function (key, result) {
                t.row.add([result['apn'], result['ip'], result['route'], button]);
                t.draw()
                //$('.dt-delete').off('click');
                //$('.dt-delete').each(function () {
                $("#data-table tbody").on('click', '.dt-delete', function (evt) {
                    therow = $(this);
                    var dtRow = therow.parents('tr');
                    var indRow = t.row(dtRow).index();
                    if (confirm("Are you sure to delete this row?")) {
                        t.row(indRow).remove().draw(false);
                    }
                });
                //});
            });
            $('#importModal').modal('hide');
        });
    });
});