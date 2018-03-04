function magnific() {
    $('.popup-gallery').magnificPopup({
        delegate: 'a',
        type: 'image',
        tLoading: 'Loading image #%curr%...',
        mainClass: 'mfp-img-mobile',
        gallery: {
            enabled: true,
            navigateByImgClick: true,
            preload: [0, 1] // Will preload 0 - before current, and 1 after the current image
        },
        image: {
            tError: '<a href="%url%">The image #%curr%</a> could not be loaded.',
            titleSrc: function(item) {
                var code = item.el.attr('data-code');
                var title = item.el.attr('title') || '';
                var tiff = item.el.attr('data-tiff');
                var epo = 'https://www.google.com/patents/' + code;
                return code + ' - ' + title + '<small><a target="_blank" href="' + tiff + '">Download TIFF</a> || <a target="_blank" href="' + epo + '">Open Patent on Google Patents</a> </small>';
            }
        }
    });
}

var images = [];
var vm, db
var PAGE_SIZE = 24;
$(document).ready(function() {
    db = new PouchDB('images');
    db.destroy().then(function(){
        db = new PouchDB('images');
        var options = {
            limit: PAGE_SIZE,
            include_docs: true
        };
        var startkey, endkey
        function getPage(response) {
            if (response && response.rows.length > 0) {
                startkey = response.rows[response.rows.length - 1].id;
                endkey = response.rows[0].id;
            } else {}
            var images = [];
            for (var i=0; i < response.rows.length; i++) {
                images.push(response.rows[i].doc)
            }
            return images;
        }

        function callPage(vm, opt) {
            vm.page = Math.max(Math.min(vm.totalPages, vm.page), 1);
            db.allDocs(opt, function(err, response) {
                console.log('>> response', response)
                vm.total = response.total_rows;
                vm.totalPages = Math.ceil(vm.total / PAGE_SIZE);
                vm.images = getPage(response);
                magnific();
            })
        }
        db.bulkDocs(patents).then(function() {
            vm = new Vue({
                el: '#galleryApp',
                data: {
                    images: images,
                    total: 0,
                    page: 0,
                    totalPages: 1
                },
                created: function () {
                    this.nextPage();
                },
                methods: {
                    nextPage: function () {
                        var self = this;
                        var opt = Object.assign({}, options, {startkey: startkey})
                        if (this.page === this.totalPages) return;
                        this.page++;
                        if (this.page > 1) opt.skip = 1;
                        console.log('> next', opt, startkey, endkey)
                        callPage(this, opt);
                    },
                    prevPage: function () {
                        var self = this;
                        var opt = Object.assign({}, options, {endkey: endkey});
                        if (this.page === 1) return;
                        this.page--;
                        if (this.page === 1) delete opt.endkey;
                        console.log('> prev', opt, startkey, endkey)
                        callPage(this, opt);
                    }
                }
            })
        });
    });
});
