/* 
 * TODO: 
 * Add rebasing
 * https://github.com/tunderdomb/rebase
 */

var {gulp, src, dest, watch, series, parallel} = require('gulp'),
    sass = require('gulp-sass')(require('sass')),
    path = require('path'),    
    browserify = require('browserify'),
    source = require('vinyl-source-stream'),
    paths = {
        // this is the starting point for the scripts.  
        // add in other scripts in this file by using the "require"
        // provided by browserfy.
        js_source: 'static_global/js_source/**/*.js',
        js: 'static_global/js_source/scripts.js',
        scss: 'static_global/sass/**/*.scss',
        css: 'static_global/css'
    };


var js_build = function (done) {
    var b = browserify({
            entries: [paths.js]
        });
    return b.bundle()
        .pipe(source('main.js'))
        .pipe(dest('static_global/js/'));
};

var style_build = function (done) {
    // Run tasks on all Sass files
    return src(paths.scss)
        .pipe(sass({
            outputStyle: 'expanded',
            sourceComments: true,
            includePaths:[
            ]
        }))
        .pipe(dest(paths.css));

};

var watch_source = function (done) {
    watch(paths.scss, series(style_build));
    watch(paths.js_source, series(js_build));
    done();
};


// gulp build
exports.build = series(
    style_build,
    js_build
);

// Default task
// gulp watch
exports.default = series(
    exports.build,
    watch_source
);