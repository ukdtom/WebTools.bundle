/*
    *** THIS FILE HAS NOTHING TO DO WITH ANGULAR ***
*/

$(function () {
    var version = 0;
    var downloadUrl = "";

    var init = function () {
        $.ajax({
            cache: false,
            global: false,
            type: 'GET',
            dataType: 'JSON',
            url: '/version',
            success: function (data) {
                version = data.version;
                $("#webtoolsVersion").html('WebTools - v' + version);
            },
            error: function (data) {
                $("#webtoolsVersion").html("WebTools not available... Please contact Devs!");
                console.log("WEBTOOLS NOT AVAILABLE!");
            }
        });
        $("#info_Download").click(downloadLatest);
        $("#login").click(login);
    }

    var downloadLatest = function () {
        document.location.href = downloadUrl;
    }

    var anyNewVersion = function (currentVersion, latestVersion) {
        currentVersion = currentVersion.split(" ")[0].toString().split('.');
        latestVersion = latestVersion.split(" ")[0].toString().split('.');
        for (var i = 0; i < (Math.max(currentVersion.length, latestVersion.length)) ; i++) {
            if (!currentVersion[i]) currentVersion[i] = 0;
            if (!latestVersion[i]) latestVersion[i] = 0;
            if (Number(currentVersion[i]) < Number(latestVersion[i])) {
                return true;
            }
        }
        return false;
    }

    var login = function () {
        var user = $('input[name="user"]').val();
        var pwd = $('input[name="pwd"]').val();

        $.ajax({
            cache: false,
            global: false,
            type: 'POST',
            url: '/login',
            data: {
                user: user,
                pwd: pwd
            },
            success: function (data) {
                $.ajax({
                    cache: false,
                    data: {
                        'module': 'git',
                        'function': 'getReleaseInfo',
                        'url': 'https://github.com/ukdtom/WebTools.bundle',
                        'version': 'latest'
                    },
                    type: 'GET',
                    datatype: 'JSON',
                    url: '/webtools2',
                    success: function (data) {
                        data = JSON.parse(data);
                        downloadUrl = data.zipball_url;
                        if (typeof (data.published_at) == 'undefined') {
                            document.location.href = '/'; //No new version available
                        } else if (anyNewVersion(version, data.tag_name)) {
                            $("#info_LocalVersion").html(version);
                            $("#info_Version").html(data.published_at);
                            $("#info_Name").html(data.name);
                            $("#info_Auther").attr("href", data.author.html_url).html(data.author.login);
                            $("#info_Notes").html(data.body);
                            $("#main").hide();
                            $("#warning").show();
                        } else {
                            document.location.href = '/'; //On latest or newer version
                        }
                    },
                    error: function () {
                        document.location.href = '/';
                    }
                });
            },
            error: function (data) {
                console.log(data);
            }
        });
    };

    init();
});