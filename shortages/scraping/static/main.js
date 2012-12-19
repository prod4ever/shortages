var App

$(function() {

    var Drug = Backbone.Tastypie.Model.extend({
        urlRoot: '/api/v1/drug/'
    });

    var DrugsList = Backbone.Tastypie.Collection.extend({
        urlRoot: '/api/v1/drug/',
        model: Drug,
        sync: function(method, model, options){  
            options.timeout = 10000;  
            options.dataType = "jsonp";  
            return Backbone.sync(method, model, options);  
        }  
    })

    var Drugs = new DrugsList()

    var DrugRow = Backbone.View.extend({
        tagName: "li",

        events: {
            "click .toggler": "open"
            //"click .button.edit":   "openEditDialog",
            //"click .button.delete": "destroy"
        },
        render: function() {
            var $toggler = $('<a class="toggler">').html(this.model.get('name'))
            this.$el.html($toggler)


            if (this.model.get('last_verified')) {
                var dateStr = moment(this.model.get('last_verified')).format('L')
            } else {
                var dateStr = 'N/A'
            } 
            var $verified = $('<span class="verified">').html(dateStr)
            this.$el.append($verified)

            var table = $('<table>')
            var header = $('<tr>')
            header.append($('<th>').html('Supplier'))
            header.append($('<th>').html('Product'))
            header.append($('<th>').html('Availability'))
            header.append($('<th>').html('Reason'))
            header.append($('<th>').html('Related Info'))
            header.append($('<th>').html('Reverified'))

            table.append(header)

            var i = 0
            _.each(this.model.get('suppliers'), function(supplier) {
                var tr = $('<tr>')
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.name.replace(/\n/g, '<br />')))
                tr.append($('<td>'))
                tr.append($('<td>'))
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.reason))
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.related_info))
                if (supplier.reverified) {
                    var dateStr = moment(supplier.reverified).format('L')
                } else {
                    var dateStr = 'N/A'
                }
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(dateStr))
                table.append(tr)

                _.each(supplier.products, function(product) {
                    var tr = $('<tr>')
                    tr.append($('<td>').html(product.name))
                    tr.append($('<td>').html(product.availability))
                    table.append(tr)
                })
                i++
            })

            this.$el.append(table)
            return this;
        },
        open: function() {
            this.$el.toggleClass('expanded')
        }
    });

    var DrugsView = Backbone.View.extend({
        el: $('#drugs'),
        pageSize: 20,
        page: 1,
        q: null,
        order_by: 'name',

        events: {
            'click #search_submit': 'onSearchClick',
            'click .next': 'next',
            'click .prev': 'prev',
            'change .order-by': 'changeOrder'
        },

        initialize: function() {
            Drugs.on('add', this.addOne, this);
            Drugs.on('reset', this.addAll, this);
            //Drugs.on('all', this.render, this);
            this.redraw()
        },
        getParams: function() {
            var params = {data: { order_by: this.order_by }}
            if (this.order_by == 'date') {
                params['data']['_order'] = 'date'
                delete params['data']['order_by']
            }
            if (this.q) params['data']['name__icontains'] = this.q
            return params
        },
        render: function() {
            console.log('render')
        },
        redraw: function() {
            Drugs.reset()
            Drugs.fetch(this.getParams())
        },
        next: function() {
            Drugs.reset()
            Drugs.fetchNext(this.getParams())
        },
        prev: function() {
            Drugs.reset()
            Drugs.fetchPrevious(this.getParams())
        },
        onSearchClick: function(e) {
            Drugs.filters.offset = 0
            this.q = $('#search').val()
            this.redraw()
        },
        changeOrder: function(e) {
            this.order_by = $(e.target).val()
            this.redraw()
        },
        addOne: function(drug) {
            var view = new DrugRow({model: drug});
            this.$('.list').append(view.render().el);
        },
        // Add all items in the **Todos** collection at once.
        addAll: function() {
            $('.current-page').html( ((Drugs.filters.offset - 20) / Drugs.filters.limit ) + 1)
            $('.total-pages').html( Math.ceil(Drugs.meta.total_count / Drugs.filters.limit ))
            this.$('.list').html('')
            Drugs.each(this.addOne, this);
        }
    })

    App = new DrugsView
})