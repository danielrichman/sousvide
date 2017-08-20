function set_status_elements(data) {
    if (data.order_name) {
        $("#order-name").text(data.order_name);
        $("#order-start-time").text(data.order_start_time);
        $("#order-end-time").text(data.order_end_time);
        $("#order-target-temperature").text(data.order_target_temperature);
    } else {
        $("#order-name").text("No current order");
        $("#order-start-time").text("");
        $("#order-end-time").text("");
        $("#order-target-temperature").text("");
    }

    $("#temperatures-reading").text(data.current_temperature || "unk");
    $("#control-log-power").text(data.control_log_power);

    $(".traffic-light").addClass("inactive");
    if (data.control_log_failed) {
        $("#traffic-light-system-failure").removeClass("inactive");
    } else if (data.order_name) {
        $("#traffic-light-cooking").removeClass("inactive");
    } else {
        $("#traffic-light-sleeping").removeClass("inactive");
    }
}

function set_all_unk() {
    $(".traffic-light").addClass("inactive");
    $("#traffic-light-system-failure").removeClass("inactive");

    $("#order-name").text("unk");
    $("#order-start-time").text("unk");
    $("#order-end-time").text("unk");
    $("#order-target-temperature").text("unk");
    $("#temperatures-reading").text("unk");
    $("#control-log-power").text("unk");
}

function get_status_update() {
    $.ajax({url: "/status", dataType: "json"})
        .done(set_status_elements)
        .fail(set_all_unk)
        .always(function () { setTimeout(get_status_update, 5000); });
}

$(get_status_update);

var chart;

function create_graph(data) {
    var config = 
        { type: 'line'
        , data: 
            { datasets:
                [ { label: "Temperature"
                  , backgroundColor: "blue"
                  , borderColor: "blue"
                  , fill: false
                  , data: data.temperatures
                  }
                , { label: "POWER"
                  , backgroundColor: "red"
                  , borderColor: "red"
                  , fill: false
                  , data: data.powers
                  }
                ]
            , options: 
                { responsive: true
                , title: { display: false, text: "Sous Vide" }
                }
            , scales: 
                { xAxes: 
                    [ { type: "time"
                      , display: true
                      , scaleLabel: { display: true, labelString: 'Date' }
                      }
                    ]
                , yAxes: 
                    [ { display: true
                      , scaleLabel: { display: true, labelString: 'value' }
                      }
                    ]
                }
            }
        };

    var ctx = $("#chart")[0].getContext("2d");
    chart = new Chart(ctx, config);
}

function get_time_series() {
    $.ajax({url: "/time-series", dataType: "json"})
        .done(create_graph)
}

$(get_time_series);
