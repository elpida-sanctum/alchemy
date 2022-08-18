$(document).ready(function () {
    var t = $('#add-table').DataTable({
        "columns": [
            { "name": "msisdn" },
            { "name": "ip" },
            { "name": "type" },
            { "name": "actions" },
        ]
    });

    $('#addRow').on('click', function () {
        var send = JSON.stringify({ 'msisdn': $('#msisdn').val(), 'ip': $('#ip').val(), 'route': $('#ip').val() })
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
                    validity[key] = val.valid;
                } else {
                    $("#" + key).removeClass('is-valid');
                    $("#" + key).addClass('is-invalid');
                    validity[key] = val.valid;
                }
            });
            console.log(validity);
            console.log(result);
            var all_valid = (validity['msisdn'] && (validity['ip'] || validity['route']));
            /*$.each(validity, function (key, value) {
                all_valid = all_valid && value;
            });*/
            if (validity['ip'] || validity['route']) {
                $("#ip").removeClass('is-invalid');
                $("#ip").addClass('is-valid');
            }
            console.log(all_valid);
            if (all_valid) {
                if (validity['ip']) {
                    t.row.add([result['msisdn'], result['ip'], "IP Address", button]);
                    t.draw()
                    $('.dt-delete').off('click');
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
                } else if (validity['route']) {
                    t.row.add([result['msisdn'], result['route'], "Route", button]);
                    t.draw()
                    $('.dt-delete').off('click');
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
                }
            }
        });

    });

    $('#sendTable').on('click', function () {
        var dataT = t.data().toArray()
        console.log(dataT)
        fetch('/api/add_msisdn', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                Connection: "close",
                Origin: "/api/add_msisdn",
            },
            body: JSON.stringify({ dataT }),
        }).then(function (response) {
            resp = response.json();
            return resp;
        }).then(function (id) {
            console.log(id);
            $.each(id, function (key, value) {
                var row = t.row(key).node();
                if (value) {
                    $(row).addClass('table-success');
                } else {
                    $(row).addClass('table-danger');
                }
            });
        });
    });

    $("#uploadFile").on('click', function () {
        var file = $('#inputFile').prop('files')[0];
        var send = new FormData();
        send.append('type', 'msisdn');
        send.append('file', file);
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
                t.row.add([result['msisdn'], result['ip'], button]);
                t.draw()
                $('.dt-delete').off('click');
                $('.dt-delete').each(function () {
                    $(this).on('click', function (evt) {
                        therow = $(this);
                        var dtRow = therow.parents('tr');
                        var indRow = t.row(dtRow).index();
                        if (confirm("Are you sure to delete this row?")) {
                            t.row(indRow).remove().draw(false);
                        }
                    });
                });
            });
            $('#importModal').modal('hide');
        });
    });
});