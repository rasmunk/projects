/**
 * Created by rasmusmunk on 27/09/2017.
 */
/*jshint esversion: 6 */
"use strict";
// The nbi_common.js file needs to be loaded before this

function createProjectTile(project) {
    var newHeader = document.createElement('h3');
    newHeader.className = "card-title";
    newHeader.innerText = project.name;

    var newBody = document.createElement('p');
    newBody.className = "card-text";
    newBody.innerText = project.description;

    var newCaption = document.createElement('div');
    newCaption.className = "caption";
    newCaption.appendChild(newHeader);
    newCaption.appendChild(newBody);

    var newImage = document.createElement('img');
    newImage.src = "/images/" + project.image;
    newImage.alt = "Project";

    var newThumb = document.createElement('div');
    newThumb.className = "thumbnail mb-4";
    newThumb.appendChild(newImage);
    newThumb.appendChild(newCaption);

    var newLink = document.createElement('a');
    newLink.className = "d-block mb-4";
    newLink.href = "/show/" + project._id;
    newLink.appendChild(newThumb);

    var newDiv = document.createElement('div');
    newDiv.className = "col-sm-6 col-md-4 col-lg-3";
    newDiv.appendChild(newLink);
    return newDiv;
}


// Login page only
function setupRequestAuth() {
    let btn = document.getElementById('btn-register');
    btn.onclick = function () {
        $('.loading-spinner').show();
        var _data = {
            'email': $('#email').val(),
            'csrf_token': $('#csrf_token').val()
        };
        $.ajax({
            url: '/request_auth',
            data: _data,
            type: 'POST',
            success: function (response) {
                $('.loading-spinner').hide();
                var flashes = document.getElementById('flashes');
                removeChildren(flashes);
                var json_response = response['data'];
                for (var key in json_response) {
                    if (json_response.hasOwnProperty(key)) {
                        var messageContainer = document.createElement('div');
                        messageContainer.setAttribute('class', "alert alert-" + key);
                        messageContainer.setAttribute('role', 'alert');
                        messageContainer.innerText = json_response[key];
                        flashes.append(messageContainer);
                    }
                }
            },
            error: function (error) {
                $('.loading-spinner').hide();
                errorRender(error);
            }
        });
    };
}

function setupResetPassword() {
    let btn = document.getElementById('btn-reset');
    btn.onclick = function () {
        $('.loading-spinner').show();
        var _data = {
            'email': $('#email').val(),
            'csrf_token': $('#csrf_token').val()
        };
        $.ajax({
            url: '/request_password_reset',
            data: _data,
            type: 'POST',
            success: function (response) {
                $('.loading-spinner').hide();
                var flashes = document.getElementById('flashes');
                removeChildren(flashes);
                var json_response = response['data'];
                for (var key in json_response) {
                    if (json_response.hasOwnProperty(key)) {
                        var messageContainer = document.createElement('div');
                        messageContainer.setAttribute('class', "alert alert-" + key);
                        messageContainer.setAttribute('role', 'alert');
                        messageContainer.innerText = json_response[key];
                        flashes.append(messageContainer);
                    }
                }
            },
            error: function (error) {
                $('.loading-spinner').hide();
                errorRender(error);
            }
        });
    };
}

// Projects page
if (location.pathname.match(/\/search$/i) || location.pathname == '/index' || location.pathname == '/my_projects') {
    $(document).ready(function () {
        setupTagSearch(createProjectTile);
    });
}

// Login page
if (location.pathname == '/login') {
    $(document).ready(function () {
        setupRequestAuth();
        setupResetPassword();
    });
}
