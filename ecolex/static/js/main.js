var _form_data = null;

$(document).ready(function () {
    // $('[data-filter]').on('click', function() {
    // 	target = $(this).data('filter')
    // 	target = $(target);
    // 	$(this).toggleClass('active');

    // 	if (target.attr('disabled')) {
    // 		target.removeAttr('disabled');
    // 	} else {
    // 		target.attr('disabled', true);
    // 	}
    // });

    // initial form value
    var _initial_form_data = $('.search-form').serialize();

    function submit() {
        var data = $('.search-form').serialize();
        if (data != _initial_form_data) {
            /*$.ajax({
                url: '/result/ajax?' + data,
                format: 'JSON',
                success: function (data) {
                    $('#layout-main').html(data.main);
                    $('#filters').html(data.sidebar);
                    _initial_form_data = data;
                    init_all();
                }
            });*/
            $('.search-form').submit();
        } else {
            console.log('No new data');
        }
    }

    function init_all() {
        // initialize tooltips
        // bootstrap tooltips are opt-in
        $('[data-toggle="tooltip"]').tooltip();

        // prevent disabled pagination anchor to trigger page reload
        $('.pagination').on('click', '.disabled', function (e) {
            e.preventDefault();
        });

        // Slider
        $("#slider-years")
          .slider()
          .on('slide', function(event) {
              var min = $('#year-min'),
                  max = $('#year-max');

              min.val(event.value[0]);
              max.val(event.value[1]);
          })
          .on('slideStop', function(event) {
            var min = $('#year-min'),
                max = $('#year-max');

            min.val(event.value[0]);
            max.val(event.value[1]);

            var form_id = $(min).data('formid');
            $(form_id).val($(min).val());

            var form_id = $(max).data('formid');
            $(form_id).val($(max).val());

            submit();
          });

        // Year inputs
        updateYear = function(e) {
          minEl = $('#year-min');
          maxEl = $('#year-max');

          min = $(minEl).val();
          max = $(maxEl).val();

          if (min == '' || typeof min == 'undefined')
            min = $(minEl).attr('min');
          if (max == '' || typeof max == 'undefined')
            max = $(maxEl).attr('max');

          console.log([min, max]);

          $("#slider-years").slider('setValue', [min, max]);
        }

        $('#year-min, #year-max').on('change', updateYear);

        // Multiselect
        $('select[multiple]').multiselect({
            buttonClass: '',
            buttonContainer: '<div class="multiselect-wrapper" />', // '<div class="btn-group multiselect-wrapper" />',
            disableIfEmpty: true,
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            // filterBehavior: 'value',
            numberDisplayed: 1,
            nonSelectedText: 'Nothing selected',
            enableCaseInsensitiveFiltering: true,
            // filterPlaceholder: "porn",
            maxHeight: 240,
            onDropdownHidden: function (e) {
                var select = $(this.$select);
                var formid = select.data('formid');

                $(formid).val(select.val());
                // submit now for now
                submit();
            },
            onDropdownShown: function(e) {
                search = $(e.target).find('.multiselect-search').focus();
            }
        });

        // Type filter - ugly
        $('.filter-type button').click(function (e) {
            var current = $('#id_type').val() || [];
            var toggle_value = $(this).data('value');
            if (current.indexOf(toggle_value) == -1) {
                current.push(toggle_value);
            } else {
                current.splice(current.indexOf(toggle_value), 1);
            }
            $('#id_type').val(current);
            // submit now for now
            submit();
        });

        // Treaty -> Type of Document/Field of application filter
        // COP Decision -> Decision Type, Decision Status /Decision Treaty
        $('input[type=checkbox]',
            $('.filter-decision, .filter-treaty')).change(function (e) {
                var current = [];
                var ul = $(this).parents('ul');
                var form_id = ul.data('formid');

                ul.find('input:checked').each(function () {
                    current.push($(this).val());
                });
                $(form_id).val(current);
                // submit now for now
                submit();
            });

        // Year controls
        $('.global-filter input[type=number]').change(function (e) {
            var form_id = $(this).data('formid');
            $(form_id).val($(this).val());
            // submit le form
            submit();
        });

        // Sortby controls
        $('.sortby').click(function (e) {
            e.preventDefault();
            var value = $(this).data('sortby');
            $('#id_sortby').val(value);
            submit();
        });

        // Reset button
        $('input[type=reset]').click(function (e) {
            e.preventDefault();
            var data = {
                'q': $('#id_q').val(),
                'type': $('#id_type').val()
            };
            $('.search-form select, .search-form input').each(function() {
                $(this).val('')
            });
            $('#id_q').val(data.q);
            $('#id_type').val(data.type);

            submit();
        });

        // Tag manager

        var states = new Bloodhound({
          name: 'animals',
          local: [{ val: 'dog' }, { val: 'pig' }, { val: 'moose' }],
          // remote: 'http://example.com/animals?q=%QUERY',
          datumTokenizer: function(d) {
            return Bloodhound.tokenizers.whitespace(d.val);
          },
          queryTokenizer: Bloodhound.tokenizers.whitespace
        });

        states.initialize();

        // var substringMatcher = function(strs) {
        //   return function findMatches(q, cb) {
        //     var matches, substrRegex;
         
        //     // an array that will be populated with substring matches
        //     matches = [];
         
        //     // regex used to determine if a string contains the substring `q`
        //     substrRegex = new RegExp(q, 'i');
         
        //     // iterate through the pool of strings and for any string that
        //     // contains the substring `q`, add it to the `matches` array
        //     $.each(strs, function(i, str) {
        //       if (substrRegex.test(str)) {
        //         // the typeahead jQuery plugin expects suggestions to a
        //         // JavaScript object, refer to typeahead docs for more info
        //         matches.push({ value: str });
        //       }
        //     });
         
        //     cb(matches);
        //   };
        // };
         
        // var states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
        //   'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii',
        //   'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
        //   'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
        //   'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
        //   'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
        //   'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
        //   'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
        //   'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
        // ];

        $('.tm-input').each(function() {
            $(this).tagsManager({
                prefilled: ['Ana', 'Alex', 'Cătălin', 'Dafina', 'Sonia', 'Valentin'],
                tagsContainer: $('<ul/>', { class: 'tm-taglist' }),
                tagCloseIcon: '',
            })
            $(this).wrap( $('<div/>', { class: 'tm-wrapper' }) );
            var label = $('<label/>', {
                'class': 'tm-label',
                'for': $(this).attr('id'),
                // 'text': $(this).attr('placeholder')
            });
            $(this).before(label);
        });
        
        // var tagApi = $('#tagManager').tagsManager({
        //     prefilled: ['Arkansas', 'Wyoming'],
        //     tagsContainer: $('<ul/>', { class: 'tm-taglist' }),
        //     // tagClass: '',
        //     tagCloseIcon: '',
        // }); 
        // $('#the-basics .typeahead').typeahead({
        //   hint: true,
        //   highlight: true,
        //   minLength: 1
        // },
        // {
        //   name: 'states',
        //   displayKey: 'value',
        //   source: states.ttAdapter()
        //   // source: substringMatcher(states)
        // }).on('typeahead:selected', function (e, d) {
        //     tagApi.tagsManager('pushTag', d.value);
        // });



    }

    init_all();
});
    