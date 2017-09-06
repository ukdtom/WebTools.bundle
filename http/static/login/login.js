/*
    *** THIS FILE HAS NOTHING TO DO WITH ANGULAR ***
*/

$(function () {
    localStorage.clear();

    var apiV3Url = "api/v3";
    var downloadUrl = "";
    var basePath = "/";

    var lang = {};

    var currentLanguage = "en";
    var currentLanguageDebug = "en";
    var passwordSet = false;
    var plexTvOnline = false;
    var version = 0;
    var wtCssTheme = "wt_csstheme";

    try {
        var locations = $(location).prop('pathname').split('/');
        if(locations[2]) basePath = "/" + locations[1] + "/";
    }
    catch (err) {
        basePath = "/";
    }

    var getTranslation = function (string) {
        $.ajax({
            cache: false,
            global: false,
            type: 'POST',
            url: apiV3Url + '/wt/getTranslate',
            data: {
                language: currentLanguage,
                string: string
            },
            success: function (data) {
                debugger;
                return data.string;
            },
            error: function (data) {
                console.log("Could not translate!! \r\n" + data);
                return string;
            }
        });
    }

    var translate = function () {
        lang = {
            loading: getTranslation("Loading..."),
            signInTowardsPlex: getTranslation("Signing in towards plex.tv"),
            useRegularPlex: getTranslation("Use your regular Plex credentials"),
            username: getTranslation("Username"),
            password: getTranslation("Password"),
            signin: getTranslation("Sign in"),
            wrongUsernamePassword: getTranslation("Wrong username and/or password"),
            newVersionAvailable: getTranslation("New Version available"),
            newVersion: getTranslation("New Version:"),
            releaseNotes: getTranslation("Release Notes:"),
            continue: getTranslation("Continue"),
            downloadLatest: getTranslation("Download Latest"),
            webtoolsNotAvailable: getTranslation("WebTools not available... Please contact Devs!")
        }

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
                var url = "api/v3/git/getReleaseInfo/url/" + encodeURIComponent("https://github.com/ukdtom/WebTools.bundle") + "/version/latest";
                $.ajax({
                    cache: false,
                    type: 'GET',
                    url: url,
                    success: function (data) {
                        data = JSON.parse(data);
                        downloadUrl = data.zipball_url;
                        if (!data.published_at) {
                            document.location.href = basePath; //No new version available
                        } else if (anyNewVersion(version, data.tag_name)) {
                            $("#info_LocalVersion").html(version);
                            $("#info_Version").html(data.published_at);
                            $("#info_Name").html(data.name);
                            $("#info_Auther").attr("href", data.author.html_url).html(data.author.login);
                            $("#info_Notes").html(data.body);
                            $("#main").hide();
                            $("#warning").show();
                        } else {
                            document.location.href = basePath; //On latest or newer version
                        }
                        webToolsLoadingEle.hide();
                    },
                    error: function (errorResp) {
                        document.location.href = basePath;
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
    
    var init = function () {
        $.ajax({
            cache: false,
            global: false,
            type: 'GET',
            dataType: 'JSON',
            url: 'version',
            success: function (data) {
                currentLanguage = data.UILanguage;
                currentLanguageDebug = data.UILanguageDebug;
                passwordSet = data.PasswordSet;
                plexTvOnline = data.PlexTVOnline;
                version = data.version;
                wtCssTheme = data.wt_csstheme;

                $("#webtoolsVersion").html('WebTools - v' + version);

                if (data[wtCssTheme]) {
                    $("#themeCSS").attr("href", "custom_themes/" + data[wtCssTheme]);
                }

                translate();
            },
            error: function (data) {
                $("#webtoolsVersion").html(lang.webtoolsNotAvailable);
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
    init();
});