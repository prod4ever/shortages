var App

$(function() {

    var Drug = Backbone.Tastypie.Model.extend({
        urlRoot: '/api/v1/drug/'
    });

    var DrugsList = Backbone.Tastypie.Collection.extend({
        urlRoot: '/api/v1/drug/',
        model: Drug
    })

    var Drugs = new DrugsList()

    var DrugRow = Backbone.View.extend({
        tagName: "li",

        events: {
            "click": "open"
            //"click .button.edit":   "openEditDialog",
            //"click .button.delete": "destroy"
        },
        render: function() {
            this.$el.html(this.model.get('name'))
            var table = $('<table>')

            console.log(this.model)
            var i = 0
            _.each(this.model.get('suppliers'), function(supplier) {
                var tr = $('<tr>')
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.name))
                tr.append($('<td>'))
                tr.append($('<td>'))
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.reason))
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.related_info))
                tr.append($('<td>', { rowspan: supplier.products.length + 1 }).html(supplier.reverified))
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
        initialize: function() {
            Drugs.on('add', this.addOne, this);
            Drugs.on('reset', this.addAll, this);
            //Drugs.on('all', this.render, this);
            Drugs.fetch({data: { order_by: 'name' }})
        },
        render: function() {
            console.log('render')
        },
        search: function(q) {
            this.$el.html('')
            Drugs.reset()
            Drugs.fetch({data: { order_by: 'name', name__contains: q }})
        },
        addOne: function(drug) {
            var view = new DrugRow({model: drug});
            this.$el.append(view.render().el);
        },
        // Add all items in the **Todos** collection at once.
        addAll: function() {
            Drugs.each(this.addOne, this);
        }
    })

    App = new DrugsView
})