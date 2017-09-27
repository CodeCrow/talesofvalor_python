/* 
 * TODO: 
 * Add rebasing
 * https://github.com/tunderdomb/rebase
 */

var gulp = require('gulp'),
    compass = require('gulp-sass'),
    path = require('path'),
    paths = {
        js: 'project_static/js/**/*.js',
        scss: 'project_static/scss/**/*.scss',
        css: 'project_static/css'
    };



gulp.task('sass', function(){
  return gulp.src(paths.scss)
    .pipe(sass())
    .pipe(gulp.dest(paths.css))
});



gulp.task('build', ['sass'], function(){

});


gulp.task('watch', function () {
    gulp.watch(paths.scss, ['sass']);
});

gulp.task('default', ['build', 'watch'], function () {

});