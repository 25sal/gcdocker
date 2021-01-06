var daemon = require("daemonize2").setup({
    main: "sched.js",
    name: "dummy_optimizer",
    pidfile: "dummy.pid"
});

switch (process.argv[2]) {

    case "start":
        daemon.start();
        break;

    case "stop":
        daemon.stop();
        break;

    default:
        console.log("Usage: [start|stop]");
}