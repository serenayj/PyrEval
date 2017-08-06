use strict;
use warnings;
use FindBin;

### 0. initialize env variables
my $home_dir = "$FindBin::Bin";
$home_dir =~ s/\/bin$//;
#print "$home_dir\n";
if (defined $ENV{'PERL5LIB'}) {
    $ENV{'PERL5LIB'} = "$ENV{PERL5LIB}:$home_dir/lib/perl";
} else {
    $ENV{'PERL5LIB'} = "$home_dir/lib/perl";
}

my $clean = 1;
my $is_train = 0;

die "Usage:  perl  test.pl  model_dir  test_file\n" if (@ARGV != 2);

my $model_dir = $ARGV[0];
#my $model_file = $ARGV[1];
my $test_file = $ARGV[1];
my $model_file = "$model_dir/model";

### 1. preprocess text
my $cmd;
$cmd = "perl  $home_dir/bin/Preprocess/preprocess.pl  $test_file  $test_file.clean";
#print "[step 1]: $cmd\n\n";
`$cmd`;


### 2. change to matlab format
$cmd = "perl  $home_dir/bin/Preprocess/change_format.pl  $model_dir  0  $test_file.clean $test_file.ind";
#print "[step 2]: $cmd\n\n";
`$cmd`;


### 3. apply ormf 
#$cmd = "matlab -nojvm -r \"path(path,'$home_dir/ormf'); test_ormf('$test_file.ind', '$model_file', '$test_file.ls')\"";
#print "[step 3]: $cmd\n\n";
#print `$cmd`;


