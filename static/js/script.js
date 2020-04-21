function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, "", -1);
}

$(function() {
    var dragging = false;

    $('body').on('touchstart', function() {
        dragging = false;
    });

    $('body').on('touchmove', function() {
        dragging = true;
        $('.menubody').removeClass('menuopen');
        $('.dropupmenu').removeClass('menuopen');
        $('#notarywatch').hide();
        $('#topnav [id^="drop"]').prop("checked", false);
        $('#notarywatchtrigger').removeClass('activetoggle');
    });

    $(document).on('touch click', function() {
        $('.menubody').removeClass('menuopen');
        $('.dropupmenu').removeClass('menuopen');
        $('#notarywatch').hide();
        $('#topnav [id^="drop"]').prop("checked", false);
        $('#notarywatchtrigger').removeClass('activetoggle');
    });

    $('#mainnav, .bottommenu:not(.datepicker), #notarywatchlist, [id^="drop"], .toggle').on('touch click', function(e) {
        e.stopPropagation();
    });

    $('.menutoggle').on('touch click', function() {
        $('.menubody').toggleClass('menuopen');
    });

    $('.dropupbutton').on('touch click', function() {
        $(this).siblings('.dropupmenu').toggleClass('menuopen');
    });

    $('#notarywatchtrigger').on('touch click', function(e) {
        e.stopPropagation();
        if ($('#notarywatch').is(":visible")) {
            $('#notarywatch').hide();
            $('#notarywatchtrigger').removeClass('activetoggle');
        } else {
            $('#notarywatch').show().css('display', 'flex');
            $('#notarywatchtrigger').addClass('activetoggle');
        }
    });

    $('#notarywatchlist').on('change', function() {
        createCookie('notarywatchlist', $(this).val(), '1825');
    });

    $('#notarywatchsave').on('touch click', function(e) {
        e.preventDefault();
        window.location.reload();
    });

    $('#notarywatch').on('submit', function(e) {
        e.preventDefault();
        window.location.reload();
    });

    function getCellValue(row, index) {
        return $(row).children('td').eq(index).text();
    }

    function getCellDataValue(row, index, datafield) {
        return $(row).children('td').eq(index).data(datafield);
    }

    function comparer(index, datafield) {
        return function(a, b) {
            if (typeof datafield !== 'undefined') {
                var valA = getCellDataValue(a, index, datafield);
                var valB = getCellDataValue(b, index, datafield);
            } else {
                var valA = getCellValue(a, index);
                var valB = getCellValue(b, index);
            }
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB);
        }
    }

    $('table:not(.biggrid) th').on('touchend click', function() {
        if (dragging)
            return;
        this.asc = this.asc || $(this).data('asc');
        var table = $(this).parents('table').eq(0);
        if ($(this).attr('data-sortby')) {
            var rows = table.find('tbody tr').toArray().sort(comparer($(this).index(), $(this).data('sortby')));
        } else {
            var rows = table.find('tbody tr').toArray().sort(comparer($(this).index()));
        }
        this.asc = (typeof this.asc == 'undefined') ? true : !this.asc;
        if (this.asc) { rows = rows.reverse(); }
        $(this).data('asc', this.asc);
        for (var i = 0; i < rows.length; i++){ table.append(rows[i]); }
    });

    $('tr').on('touchend click', function(e) {
        if (dragging)
            return;

        if($(e.target).closest('a').length) {
            return true;
        }
        e.preventDefault();

        if ($(this).attr('data-ac') && $(this).attr('data-notaryname')) {
            window.location.href='/notary/node/' + $(this).data('notaryname') + '/smartchain/' + $(this).data('ac');
        } else if ($(this).attr('data-ac')) {
            window.location.href='/smartchain/' + $(this).data('ac');
        } else if ($(this).attr('data-notaryname')) {
            window.location.href='/notary/node/' + $(this).data('notaryname');
        } else if ($(this).attr('data-txid')) {
            window.open('https://kmdexplorer.io/tx/' + $(this).data('txid'));
        } else if ($(this).attr('data-hash')) {
            window.open('https://blockchain.com/btc/tx/' + $(this).data('hash'));
        } else if ($(this).attr('data-miner')) {
            window.location.href='/mining/notary/' + $(this).data('miner');
        } else if ($(this).attr('data-votetxid')) {
            window.open('http://vote2.explorer.supernet.org/tx/' + $(this).data('votetxid'));
        }
    });

    $('th').on('touchend click', function(e) {
        if (dragging)
            return;
        e.preventDefault();
        if ($(this).attr('data-notaryname')) {
            window.location.href='/notary/node/' + $(this).data('notaryname');
        }
    });

    /*
    $('[data-tooltip]').on('mouseover', function() {
        var thisoffset = $(this).position();
        var tiptop = thisoffset.top-30;

        $(this).append('<div class="tooltip" style="top:' + tiptop + 'px;">' + $(this).data('tooltip') + '</div>');
    });

    $('[data-tooltip]').on('mouseout', function() {
        $('.tooltip').remove();
    });
    */

    $('.biggrid td').hover(
        function() {
            $(this).closest('table').find('td:nth-child(' + ($(this).index()+1) + ')').addClass('columnhover');
            $(this).closest('table').find('thead th:nth-child('  + ($(this).index()+1) + ')').addClass('columnhover');
            var tooltipoffset = $('th.columnhover > div').offset();
            var tooltipwidth = $('th.columnhover > div').width();
            var rightside = tooltipoffset.left + tooltipwidth;
            var windowwidth = $(window).width();
            var windowoffset = $(window).scrollLeft();
            var newoffset = windowwidth + windowoffset - tooltipwidth - 20;
            if (rightside > windowwidth + windowoffset) {
                $('th.columnhover > div').css({ left: newoffset });
            }
        },
        function() {
            $(this).closest('table').find('td:nth-child(' + ($(this).index()+1) + ')').removeClass('columnhover');
            $(this).closest('table').find('thead th:nth-child('  + ($(this).index()+1) + ')').removeClass('columnhover');
            $('.biggrid thead th.rotate > div').css({ left: "" });
        }
    );

    if ($('#datefilter').length >0) {
        var localdate = new Date();
        //var utctoday = new Date(localdate.getTime() + localdate.getTimezoneOffset() * 60000).toJSON().slice(0, 10);
        //console.log(localdate.toJSON().slice(0, 10));
        //console.log(utctoday);

        if (selectedday.length < 1) {
            selectedday = utctoday;
        }

        $.datepicker._gotoTodayOriginal = $.datepicker._gotoToday;
        $.datepicker._gotoToday = function(id) {
            //window.location.href='./?day=' + utctoday;
            window.location.href='/nn/day/today';
        };

        $('#datefilter').datepicker({
            duration: 'fast',
            dateFormat: 'yy-mm-dd',
            changeMonth: true,
            defaultDate: selectedday,
            minDate: startedday,
            maxDate: utctoday,
            showButtonPanel: true,
            closeText: 'Close',
            onSelect: function(date, obj) {
                var utcdate = new Date(date + ' ' + localdate.getHours() + ':' + localdate.getMinutes() + ':' + localdate.getSeconds()).toJSON().slice(0, 10);
                //console.log('utcdate:' + utcdate);
                //setTimeout(function() {
                    window.location.href='/nn/day/' + date;
                //}, 5000);
            },
            beforeShow: function( input ) {
                setTimeout(function() {
                    if( !$('#datepickerall').length ) {
                        var buttonPane = $( input )
                            .datepicker( "widget" )
                            .find( ".ui-datepicker-buttonpane" );

                        $('<button>', {
                            id: 'datepickerall',
                            text: "All",
                            click: function() {
                                window.location.href='/nn';
                            }
                        }).appendTo( buttonPane ).addClass("ui-datepicker-clear ui-state-default ui-priority-primary ui-corner-all");
                    }

                    $('.ui-datepicker-today a.ui-state-highlight').removeClass('ui-state-highlight');
                }, 1 );
            },
        });

        $(".dropupbutton.datepicker").on('click touch mouseover', function() {
            $("#datefilter").datepicker("show");
        });
    }

    var refresherdefault = 300000;
    var refresher = readCookie('refresher');
    var refreshertimeout;
    var refreshercountdown;
    $('#refresher').on('touch click', function() {
        if (!refresher) {
            refresher = 1;
            createCookie('refresher', refresher, '1825');
            refreshertimeout = setTimeout(function() {
                window.location.reload();
            }, refresherdefault);
            refreshercountdown = setInterval(function() {
                var currentms = $('#refresher').data('ms');
                currentms = currentms - 1000;
                $('#refresher').data('ms', currentms);
                $('#refresher').prop('title', (currentms / 1000) + 's');
            }, 1000);
            $(this).addClass('refresheron');
        } else {
            refresher = false;
            eraseCookie('refresher');
            clearTimeout(refreshertimeout);
            clearInterval(refreshercountdown);
            $(this).removeClass('refresheron');
            $(this).data('ms', refresherdefault);
            $(this).prop('title', (refresherdefault / 1000) + 's');
        }
    });

    if ((typeof autorefresh == 'undefined' || autorefresh) && refresher) {
        refreshertimeout = setTimeout(function() {
            window.location.reload();
        }, refresherdefault);
        refreshercountdown = setInterval(function() {
            var currentms = $('#refresher').data('ms');
            currentms = currentms - 1000;
            $('#refresher').data('ms', currentms);
            $('#refresher').prop('title', (currentms / 1000) + 's');
        }, 1000);
        $('#refresher').addClass('refresheron');
    }
});