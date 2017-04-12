/*
    *** THIS FILE HAS NOTHING TO DO WITH ANGULAR ***
*/

$(function () {
    var version = 0;
    var downloadUrl = "";
    var wtCssTheme = "wt_csstheme";

    var init = function () {
        $.ajax({
            cache: false,
            global: false,
            type: 'GET',
            dataType: 'JSON',
            url: 'version',
            success: function (data) {
                version = data.version;
                $("#webtoolsVersion").html('WebTools - v' + version);

                if (data[wtCssTheme]) {
                    $("#themeCSS").attr("href", "custom_themes/" + data[wtCssTheme]);
                }
            },
            error: function (data) {
                $("#webtoolsVersion").html("WebTools not available... Please contact Devs!");
                console.log("WEBTOOLS NOT AVAILABLE!");
            }
        });

        $("#info_Download").click(downloadLatest);
        $("#login").click(login);

        $('input[name="user"]').focus();
        $(document).keypress(function (e) {
            if (e.which == 13) {
                login();
            }
        });
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
            if (Number(currentVersion[i]) > Number(latestVersion[i])) {
                return false;
            }
        }
        return false;
    }

    var login = function () {
        var user = $('input[name="user"]').val();
        var pwd = $('input[name="pwd"]').val();
        var webToolsLoadingEle = $("webtools-loading");
        webToolsLoadingEle.show();

        $.ajax({
            cache: false,
            global: false,
            type: 'POST',
            url: 'login',
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
                    url: 'webtools2',
                    success: function (data) {
                        data = JSON.parse(data);
                        downloadUrl = data.zipball_url;
                        if (!data.published_at) {
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
                        webToolsLoadingEle.hide();
                    },
                    error: function (errorResp) {
                        document.location.href = '/';
                        webToolsLoadingEle.hide();
                    }
                });
            },
            error: function (errorResp) {
                webToolsLoadingEle.hide();
                var error = $("#error");
                var wrong = $("#wrong");
                error.hide();
                wrong.hide();
                if (errorResp.status === 401 || errorResp.status === 412) {
                    wrong.show();
                } else {
                    error.html("Error occurred! " + (errorResp.responseText ? errorResp.responseText : "No error msg!"));
                    error.show();
                    console.log(errorResp);
                }
            }
        });
    };

    init();
});