/*
    *** THIS FILE HAS NOTHING TO DO WITH ANGULAR ***
*/

$(function () {
    localStorage.clear();
    
    var downloadUrl = "";
    var basePath = "/";

    var lang;
    var translationsTodo = 1;

    var currentLanguage = "en";
    var currentLanguageDebug = "en";
    var passwordSet = false;
    var plexTvOnline = false;
    var version = 0;
    var wtCssTheme = "wt_csstheme";
    
    var plexOnlineEle = $("#plexOnlineContainer");
    var plexOfflineEle = $("#plexOfflineContainer");
    var signInLocalPasswordEle = $("#signInLocalPassword");
    var createLocalPasswordEle = $("#createLocalPassword");
    var usernameEle = $("#usernameContainer");
    var passwordEle = $("#passwordContainer");
    var rePasswordEle = $("#repasswordContainer");

    var wrongUsernamePassword = $("#wrongUsernamePassword");
    var wrongPassword = $("#wrongPassword");
    var passwordDoesntMatch = $("#passwordDoesntMatch");

    try {
        var locations = $(location).prop('pathname').split('/');
        if(locations[2]) basePath = "/" + locations[1] + "/";
    }
    catch (err) {
        basePath = "/";
    }

    var processTranslation = function() {
        if (translationsTodo === 0) {
            $("#signInTowardsPlex").html(lang.signInTowardsPlex);
            $("#useRegularPlex").html(lang.useRegularPlex);
            $("#plexIsOffline").html(lang.plexIsOffline);
            $("#signInLocalPassword").html(lang.signInLocalPassword);
            $("#createLocalPassword").html(lang.createLocalPassword);
            $("#username").html(lang.username);
            $("input[name=user]").attr("placeholder", lang.username);
            $("#password").html(lang.password);
            $("input[name=pwd]").attr("placeholder", lang.password);
            $("#passwordagain").html(lang.passwordagain);
            $("input[name=repwd]").attr("placeholder", lang.passwordagain);
            $("#login").val(lang.signin);
            if (!plexTvOnline && !passwordSet) $("#login").val(lang.createPassword); 
            $("#wrongUsernamePassword").html(lang.wrongUsernamePassword);
            $("#wrongPassword").html(lang.wrongPassword);
            $("#passwordDoesntMatch").html(lang.passwordDoesntMatch);
            $("#newVersionAvailable").html(lang.newVersionAvailable);
            $("#newVersion").html(lang.newVersion);
            $("#releaseNotes").html(lang.releaseNotes);
            $("#info_Continue").html(lang.continue);
            $("#info_Download").html(lang.downloadLatest);
        }
    }

    var getTranslation = function (key, string) {
        $.ajax({
            cache: false,
            global: false,
            type: 'POST',
            url: 'getTranslate',
            data: JSON.stringify({
                "language": currentLanguage,
                "string": string
            }),
            success: function (translatedString) {
                lang[key] = translatedString;
            },
            error: function (data) {
                console.log("Could not translate!! \r\n" + data);
            },
            complete: function(data) {
                translationsTodo--;
                processTranslation();
            }
        });
    }

    var translate = function () {
        lang = {
            //loading: "Loading...", //Can't implement for now (Need to change to loading spinner because the translation will be picked up by an async call)
            signInTowardsPlex: "Signing in towards plex.tv",
            useRegularPlex: "Use your regular Plex credentials",
            plexIsOffline: "PMS is not connected to plex.tv",
            signInLocalPassword: "Sign in with your local password",
            createLocalPassword: "Create a local password",
            username: "Username",
            password: "Password",
            passwordagain: "Password again",
            signin: "Sign in",
            createPassword: "Create password",
            wrongUsernamePassword: "Wrong username and/or password",
            wrongPassword: "Wrong password",
            passwordDoesntMatch: "The passwords does not match",
            newVersionAvailable: "New Version available",
            newVersion: "New Version:",
            releaseNotes: "Release Notes:",
            continue: "Continue",
            downloadLatest: "Download Latest",
            webtoolsNotAvailable: "WebTools not available... Please contact Devs!"
        }

        translationsTodo = Object.keys(lang).length;
        for (var key in lang) {
            if (!lang.hasOwnProperty(key)) return;
            var item = lang[key];

            getTranslation(key, item);
        }
    }

    var hideWarning = function () {
        wrongUsernamePassword.hide();
        wrongPassword.hide();
        passwordDoesntMatch.hide();
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

        if (!plexTvOnline && !passwordSet) {
            var repwd = $('input[name="repwd"]').val();

            if (pwd !== repwd) {
                hideWarning();
                passwordDoesntMatch.show();
                return;
            }
        }

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
                error.hide();
                hideWarning();
                if (errorResp.status === 401 || errorResp.status === 412) {
                    if (plexTvOnline) wrongUsernamePassword.show();
                    else wrongPassword.show();
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
                if (plexTvOnline) {
                    plexOnlineEle.show();
                    plexOfflineEle.hide();
                    usernameEle.show();
                    passwordEle.show();
                    rePasswordEle.hide();
                } else {
                    plexOnlineEle.hide();
                    plexOfflineEle.show();
                    usernameEle.hide();
                    passwordEle.show();
                    
                    if (passwordSet) {
                        rePasswordEle.hide();
                        signInLocalPasswordEle.show();
                        createLocalPasswordEle.hide();
                    } else {
                        rePasswordEle.show();
                        signInLocalPasswordEle.hide();
                        createLocalPasswordEle.show();
                    }
                }

                $("#webtoolsVersion").html('WebTools - v' + version);

                if (data.wt_csstheme) {
                    $("#themeCSS").attr("href", "custom_themes/" + data.wt_csstheme);
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

        setTimeout(function () {
            $('input[name="user"]').focus();
        }, 500)
        $(document).keypress(function (e) {
            if (e.which === 13) {
                login();
            }
        });
    }
    init();
});