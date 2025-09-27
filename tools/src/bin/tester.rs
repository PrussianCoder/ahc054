#![allow(non_snake_case)]

use std::process::Stdio;
use tools::*;

fn main() {
    if std::env::args().len() < 2 {
        eprintln!(
            "Usage: {} <command> [<args>...]",
            std::env::args().nth(0).unwrap()
        );
        return;
    }
    let (command, args) = (
        std::env::args().nth(1).unwrap(),
        std::env::args().skip(2).collect::<Vec<_>>(),
    );
    let mut p = std::process::Command::new(command)
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap_or_else(|e| {
            eprintln!("failed to execute the command");
            eprintln!("{}", e);
            std::process::exit(1)
        });
    match exec(&mut p, true) {
        Ok((input, output)) => {
            let (score, err) = compute_score(&input, &output);
            if err.starts_with("Not reachable") {
                eprintln!("{}", err);
            } else if err != "" {
                panic!("An internal error has occurred. Please contact the organizers via clar.");
            }
            eprintln!("Score = {}", score);
        }
        Err(err) => {
            if let Ok(Some(status)) = p.try_wait() {
                if !status.success() {
                    std::process::exit(1);
                }
            }
            let _ = p.kill();
            eprintln!("{}", err);
            eprintln!("Score = 0");
        }
    }
}
